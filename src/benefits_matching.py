from typing import TypedDict, List, Optional, Any
from langgraph.graph import StateGraph, END
from langchain_core.messages import HumanMessage, SystemMessage
from src.benefits_state import BenefitsState
from src.schemas import BenefitsAnalysisOutput, CitizenProfile
from src.agents import llm
from src.rag import get_retriever
from src.logger import setup_logger
from src.cache_helper import CacheHelper

logger = setup_logger("BenefitsAgent")

# --- Prompts ---

PROFILE_EXTRACTION_PROMPT = """
Extract citizen profile information from the user's query.
Look for: age, income, category/caste, location, education level, employment status, family size, special conditions.

User query: {query}

If information is missing, leave it as null.
"""

# ENHANCED: Gold Standard Benefits Matching with Priority Ranking
BENEFITS_MATCHING_PROMPT = """
You are a Benefits Discovery Expert with a "life-first" approach.
Based on the citizen profile and retrieved policy documents, identify ALL benefits the citizen qualifies for.

Citizen Profile:
{profile}

Policy Context:
{context}

User Question:
{query}

**PRIORITY RANKING SYSTEM:**
Categorize each benefit into one of three tiers:
1. 🟢 HIGH PRIORITY - Benefits they clearly qualify for, can apply immediately
2. 🟡 SECONDARY - Benefits they likely qualify for but need document verification or additional info
3. 🔵 FUTURE - Benefits they could qualify for in future or with changed circumstances

**MULTI-LEVEL AGGREGATION (Remove Silos):**
Include ALL applicable schemes from:
- Central Government schemes
- State Government schemes (for their location: {location})
- Local/Municipal schemes
- NGO/CSR programs (if known)

For EACH benefit, provide:
1. **What You Get**: Clear description of the benefit amount/service
2. **Why You Qualify**: Specific criteria match (e.g., "You qualify because your income is below ₹X and you are aged Y")
3. **What's Needed Next**: Immediate next step + required documents
4. **Urgency**: How quickly to act (deadline if known)
5. **Confidence**: How confident we are in eligibility (high/medium/low)

**RECOMMENDATION STRATEGY:**
At the end, provide a personalized recommendation:
- "If you want the fastest support, start with [Scheme A]"
- "If long-term impact matters more, prioritize [Scheme B]"

Provide a comprehensive analysis prioritizing high-impact, high-confidence benefits first.
"""

# ENHANCED: Synthesis with Trust-Backed Recommendations
SYNTHESIS_PROMPT = """
You are a Benefits Advisor using a life-first, trust-building approach.
Based on the benefits analysis below, create a clear, actionable Markdown guide.

**LANGUAGE INSTRUCTION:**
The user has selected language: '{language}'.
- You MUST respond in '{language}'.
- Translate all headers, benefit descriptions, and instructions to '{language}'.
- Keep technical terms in English if translation would cause confusion, but explain them.

ANALYSIS:
{analysis}

REQUIREMENTS:
1. **Summary**: Start with "🎯 Great news! You may qualify for X benefits!"

2. **Organize by Priority**:
   
   ### 🟢 Start Here (High Priority)
   [List high-confidence, immediately applicable benefits]
   
   ### 🟡 Worth Exploring (Secondary)
   [List benefits needing verification]
   
   ### 🔵 Keep in Mind (Future)
   [List future possibilities]

3. **For each benefit include**:
   - **What it is** (1-2 sentences)
   - **Why you qualify** (specific criteria match)
   - **What's needed next** (single clear action step)
   - **Documents needed** (checklist format)
   - **Deadline** (if applicable)

4. **Strategy Recommendation**:
   💡 **My Recommendation**: If you want fast results, start with [X]. For maximum long-term benefit, prioritize [Y].

5. **Formatting**:
   - Use emojis for visual clarity
   - Use checkboxes for document lists
   - Highlight urgent items with ⚠️
   - Warn about conflicts if any

6. **Trust Building**:
   - End with "Ready to apply? I can guide you step-by-step through any of these."

Output ONLY the Markdown response.
"""

# --- Nodes ---

def profile_extraction_node(state: BenefitsState):
    logger.info("Extracting citizen profile...")
    query = state["input_text"]
    try:
        structured_llm = llm.with_structured_output(CitizenProfile)
        prompt = PROFILE_EXTRACTION_PROMPT.format(query=query)
        
        profile = structured_llm.invoke([HumanMessage(content=prompt)])
        return {"citizen_profile": profile}
    except Exception as e:
        logger.error(f"Profile extraction failed: {e}")
        return {"citizen_profile": None}

def benefits_matching_node(state: BenefitsState):
    logger.info("Matching benefits...")
    query = state["input_text"]
    profile = state.get("citizen_profile")
    
    # RAG retrieval using agent
    try:
        from src.rag_agent import rag_agent_retrieve
        context = rag_agent_retrieve(query)
    except Exception as e:
        logger.warning(f"RAG Agent failed: {e}")
        context = "No specific policy documents found."
    
    if profile:
        profile_str = str(profile.model_dump())
        location = profile.location or "Unknown"
    else:
        profile_str = "No profile"
        location = "Unknown"
    
    # Check cache
    cache_key = CacheHelper.hash_query(query, profile_str + context[:200])
    cached_result = CacheHelper.get_llm_cache(cache_key)
    if cached_result:
        logger.info("Using cached benefits result")
        return {"analysis_output": cached_result}
    
    try:
        structured_llm = llm.with_structured_output(BenefitsAnalysisOutput)
        prompt = BENEFITS_MATCHING_PROMPT.format(profile=profile_str, context=context, query=query, location=location)
        
        analysis = structured_llm.invoke([HumanMessage(content=prompt)])
        
        # Cache result
        CacheHelper.set_llm_cache(cache_key, analysis)
        
        return {"analysis_output": analysis}
    except Exception as e:
        logger.error(f"Benefits matching failed: {e}")
        return {"analysis_output": None}

def synthesis_node(state: BenefitsState):
    logger.info("Synthesizing benefits guide...")
    analysis = state.get("analysis_output")
    language = state.get("language", "en")
    
    if not analysis:
        return {"final_markdown_response": "I'm sorry, I couldn't identify benefits at this moment."}
    
    try:
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

def build_benefits_graph():
    workflow = StateGraph(BenefitsState)
    
    workflow.add_node("profile_extraction", profile_extraction_node)
    workflow.add_node("benefits_matching", benefits_matching_node)
    workflow.add_node("synthesis", synthesis_node)
    
    workflow.set_entry_point("profile_extraction")
    workflow.add_edge("profile_extraction", "benefits_matching")
    workflow.add_edge("benefits_matching", "synthesis")
    workflow.add_edge("synthesis", END)
    
    return workflow.compile()

benefits_graph = build_benefits_graph()
