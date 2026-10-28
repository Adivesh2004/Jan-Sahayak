from typing import TypedDict, List, Optional, Any
from langgraph.graph import StateGraph, END
from langchain_core.messages import HumanMessage, SystemMessage
from src.interpretation_state import InterpretationState
from src.schemas import PolicyAnalysisOutput
from src.agents import llm
from src.rag import get_retriever
from src.logger import setup_logger
from src.cache_helper import CacheHelper

logger = setup_logger("PolicyNavigator")

# --- Prompts ---

INTENT_Prompt = """
Analyze the user's input and identifying their core intent regarding the policy.
Possible intents: 
- "policy_explanation": Wants to know what the policy says.
- "eligibility_check": Wants to know if they qualify.
- "benefit_analysis": Wants to know what they get.
- "obligation_analysis": Wants to know what they must do.
- "risk_analysis": Wants to know risks or ambiguities.

Return ONLY the intent string.
"""

EXTRACTION_PROMPT = """
You are a Policy Extraction Expert.
Analyze the provided policy text and extract structured information into the required JSON format.
Focus on:
1. Eligibility Rules (conditions, exceptions)
2. Benefits (what is given)
3. Obligations (what must be done)
4. Risks (ambiguities, missing info)
5. Metadata (authority, jurisdiction)

Input Policy Context:
{context}

User Query:
{query}
"""

SYNTHESIS_PROMPT = """
You are the Policy Navigator. 
Based on the structured analysis below, provide a clear, easy-to-understand Markdown response for the user.

**LANGUAGE INSTRUCTION:**
The user has selected language: '{language}'.
- You MUST respond in '{language}'.
- Translate all headers and explanations to '{language}'.
- Keep technical terms in English if translation would cause confusion, but explain them.

STRUCTURED ANALYSIS:
{analysis}

REQUIREMENTS:
1. Use simple, plain language. Avoid jargon.
2. Structure with clear headers (e.g., "Am I Eligible?", "What do I get?").
3. Highlight risks or missing information clearly.
4. Be helpful and direct.
5. If the user asked a specific question, answer it directly first.

Output ONLY the Markdown response.
"""

# --- Nodes ---

def intent_node(state: InterpretationState):
    logger.info("Detecting intent...")
    query = state["input_text"]
    try:
        response = llm.invoke([
            SystemMessage(content=INTENT_Prompt),
            HumanMessage(content=query)
        ])
        intent = response.content.strip().lower()
        # Fallback normalization
        if "eligibility" in intent: intent = "eligibility_check"
        elif "benefit" in intent: intent = "benefit_analysis"
        elif "risk" in intent: intent = "risk_analysis"
        else: intent = "policy_explanation"
        
        logger.info(f"Detected intent: {intent}")
        return {"intent": intent}
    except Exception as e:
        logger.error(f"Intent detection failed: {e}")
        return {"intent": "policy_explanation"}

def rag_node(state: InterpretationState):
    logger.info("Retrieving documents via RAG Agent...")
    query = state["input_text"]
    try:
        # Use agentic RAG instead of direct retriever
        from src.rag_agent import rag_agent_retrieve
        
        result = rag_agent_retrieve(query)
        
        # Convert string result back to document-like format for compatibility
        from langchain_core.documents import Document
        docs = [Document(page_content=result)]
        
        logger.info(f"RAG Agent completed retrieval.")
        return {"retrieved_docs": docs}
    except Exception as e:
        logger.error(f"RAG Agent failed: {e}")
        return {"retrieved_docs": []}

def extraction_node(state: InterpretationState):
    logger.info("Extracting structured policy data...")
    query = state["input_text"]
    docs = state.get("retrieved_docs", [])
    
    context = "\n\n".join([d.page_content for d in docs])
    if not context:
        context = "No specific policy documents found. Answer based on general knowledge if possible, or state that info is missing."

    # Check cache
    cache_key = CacheHelper.hash_query(query, context[:200])  # Use first 200 chars of context
    cached_result = CacheHelper.get_llm_cache(cache_key)
    if cached_result:
        logger.info("Using cached extraction result")
        return {"analysis_output": cached_result}

    try:
        structured_llm = llm.with_structured_output(PolicyAnalysisOutput)
        prompt = EXTRACTION_PROMPT.format(context=context, query=query)
        
        analysis = structured_llm.invoke([HumanMessage(content=prompt)])
        
        # Cache the result
        CacheHelper.set_llm_cache(cache_key, analysis)
        
        return {"analysis_output": analysis}
    except Exception as e:
        logger.error(f"Extraction failed: {e}")
        return {"analysis_output": None}

def synthesis_node(state: InterpretationState):
    logger.info("Synthesizing final response...")
    analysis = state.get("analysis_output")
    language = state.get("language", "en")
    
    if not analysis:
        return {"final_markdown_response": "I'm sorry, I couldn't analyze the policy details at this moment. Please try again."}
    
    try:
        # Convert Pydantic model to dict for prompt injection
        analysis_dict = analysis.model_dump()
        prompt = SYNTHESIS_PROMPT.format(analysis=str(analysis_dict), language=language)
        
        response = llm.invoke([HumanMessage(content=prompt)])
        return {
            "final_markdown_response": response.content,
            "final_json_response": analysis_dict
        }
    except Exception as e:
        logger.error(f"Synthesis failed: {e}")
        return {"final_markdown_response": "Error generating response."}

# --- Graph Construction ---

def build_policy_navigator():
    workflow = StateGraph(InterpretationState)
    
    workflow.add_node("intent_node", intent_node)
    workflow.add_node("rag_node", rag_node)
    workflow.add_node("extraction_node", extraction_node)
    workflow.add_node("synthesis_node", synthesis_node)
    
    # Linear flow for V1
    workflow.set_entry_point("intent_node")
    workflow.add_edge("intent_node", "rag_node")
    workflow.add_edge("rag_node", "extraction_node")
    workflow.add_edge("extraction_node", "synthesis_node")
    workflow.add_edge("synthesis_node", END)
    
    return workflow.compile()

policy_navigator_graph = build_policy_navigator()
