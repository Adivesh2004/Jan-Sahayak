"""
Conversation Agent - Life-First Citizen Discovery
Implements empathetic, conversational approach to understand citizen needs
before diving into policy jargon.

Key Principles:
- Life-first, not policy-first
- Build trust before asking sensitive questions
- Progressive profiling (not all questions at once)
- Always explain "why" we're asking
"""
from typing import Dict, Any, List, Optional
from langgraph.graph import StateGraph, END
from langchain_core.messages import HumanMessage, AIMessage
from src.conversation_state import ConversationState, get_initial_conversation_state, CONVERSATION_PHASES
from src.config import get_zynd_agent
from src.logger import setup_logger
from src.rag_agent import rag_agent_retrieve
from src.question_config import get_all_option_questions
from src.languages import TRANSLATIONS

logger = setup_logger("ConversationAgent")

# --- Conversation Nodes ---

def entry_node(state: ConversationState) -> Dict[str, Any]:
    """Initial entry point - greet and setup questions"""
    logger.info("Conversation Agent: Entry phase")
    
    phase = state.get("conversation_phase", "entry")
    
    # If already in discovery, pass through
    if phase != "entry":
        return {}
    
    language = state.get("language", "en")
    
    # load dynamic questions for the language
    all_questions = get_all_option_questions(language)
    entry_msg = "Namaste! I am your Jan Sahayak. How can I help you today?"
    
    # Skip Discovery - Go straight to Chat/Recommendation
    return {
        "conversation_phase": "recommendation", # Reuse recommendation phase as main chat
        "current_response": entry_msg,
        "session_trust_level": 0.5,
        "last_agent_step": "entry"
    }


def recommendation_node(state: ConversationState) -> Dict[str, Any]:
    """Main Chat Node - RAG + Contextual Q&A"""
    logger.info("Conversation Agent: Chat/Recommendation phase")
    
    input_text = state.get("input_text", "")
    chat_history = state.get("chat_history", [])
    language = state.get("language", "en")
    
    # 1. Contextualize Query (Rewrite for RAG)
    query = input_text
    from src.agents import llm
    
    if chat_history:
        REWRITE_PROMPT = """
Given a chat history and the latest user question which might reference context in the history, formulate a standalone question which can be understood without the chat history. Do NOT answer the question, just rewrite it if needed, otherwise return it as is.

Chat History:
{history}

Latest Question: {input}

Standalone Question:
"""
        try:
             history_str = "\n".join(chat_history[-6:]) # Use last 3 turns
             prompt = REWRITE_PROMPT.format(history=history_str, input=input_text)
             msg = llm.invoke([HumanMessage(content=prompt)])
             query = msg.content.strip()
             logger.info(f"Contextualized Query: {input_text} -> {query}")
        except Exception as e:
             logger.error(f"Query rewrite failed: {e}")
             query = input_text

    logger.info(f"Final RAG query: {query}")
    
    # 2. RAG Retrieval using rewritten query
    from src.rag_agent import rag_agent_retrieve
    try:
        context = rag_agent_retrieve(query)
    except Exception as e:
        logger.error(f"RAG error: {e}")
        context = ""
    
    # Chat Prompt
    CHAT_PROMPT = """
You are 'Jan Sahayak', a helpful AI assistant for Indian Government Schemes.
Your goal is to answer the user's questions clearly and helpfully based on the context.

**LANGUAGE INSTRUCTION:**
The user has selected language: '{language}'.
- You MUST respond in '{language}'.

**CONTEXT:**
{context}

**CHAT HISTORY:**
{history}

**USER QUESTION:**
{input}

**INSTRUCTIONS:**
1. Answer the user's question directly.
2. Use the provided Context to give accurate details about schemes/policies.
3. Use Chat History to understand follow-up questions (e.g., "how do I apply for *that*?").
4. If you don't know, say so politely and suggest contacting a local office.
5. Format with Markdown (bold, lists).
"""
    try:
        from src.agents import llm
        
        # Format history string
        history_str = "\n".join(chat_history[-10:]) if chat_history else "No history."
        
        prompt = CHAT_PROMPT.format(
            language=language,
            context=context,
            history=history_str,
            input=input_text
        )
        
        logger.info("Generating chat response...")
        response_msg = llm.invoke([HumanMessage(content=prompt)])
        response = response_msg.content
        confidence = 0.8 if context else 0.5
        
    except Exception as e:
        logger.error(f"Chat generation failed: {e}")
        response = "I encountered an error. Please try asking again."
        confidence = 0.0

    return {
        "conversation_phase": "recommendation",
        "final_markdown_response": response,
        "current_response": response,
        "recommendation_confidence": confidence
    }


def synthesis_node(state: ConversationState) -> Dict[str, Any]:
    """Final synthesis and response formatting"""
    logger.info("Conversation Agent: Synthesis")
    
    response = state.get("current_response", "")
    
    if not response:
        response = state.get("final_markdown_response", "I'm here to help. What would you like to know?")
    
    return {
        "final_markdown_response": response
    }


# --- Graph Router ---

def route_conversation(state: ConversationState) -> str:
    """Route based on conversation phase"""
    phase = state.get("conversation_phase", "entry")
    
    if phase == "entry":
        # Entry node generated greeting -> Stop for input
        return END
    elif phase == "discovery":
        # Discovery node generated question -> Stop for input
        return END
    elif phase == "recommendation":
        # Move to synthesis
        return "synthesis"
    else:
        return END


# --- Build Graph ---

conversation_workflow = StateGraph(ConversationState)

# Add nodes
conversation_workflow.add_node("entry", entry_node)
# conversation_workflow.add_node("discovery", discovery_node) # Removed
conversation_workflow.add_node("recommendation", recommendation_node)
conversation_workflow.add_node("synthesis", synthesis_node)

# Set entry point
conversation_workflow.set_entry_point("entry")

# Add edges
# Logic: 
# 1. Entry -> Router (Check phase)
#    - If Phase=Discovery (just switched): Router -> END (Wait for user)
#      Wait, if Entry switched to Discovery, it means Entry ran.
#      Entry returns greeting.
#      Router returns END.
# 2. Next turn: Resume.
#    Since we don't have checkpointer here, we rely on 'run_conversation' re-invoking.
#    State passed in has phase="discovery".
#    Entry node logic: if phase!=entry, return {}.
#    So Entry node does nothing.
#    Router checks phase="discovery". Returns END?
#    NO. If Router returns END, Discovery node NEVER RUNS.
#    We need Router to send "discovery" -> "discovery_node".
    
# FIX ROUTER LOGIC:
# If phase="entry" (after EntryNode ran and kept it entry? No, EntryNode sets discovery).
# EntryNode sets "discovery".
# Router sees "discovery".
# It must decide: Did we just generate a greeting? Or are we processing input?
# EntryNode returns `current_response` = Greeting.
# So if we have `current_response` populated, maybe we stop?
# But `discovery_node` also populates `current_response`.

# New Edge Logic:
# Entry -> Conditional(route_entry)
# Discovery -> Conditional(route_discovery)

conversation_workflow.add_conditional_edges(
    "entry",
    lambda x: "end_turn" if x.get("conversation_phase") == "discovery" else "discovery" 
    # Wait, if Entry changes phase to Discovery, we want to End Turn (show greeting).
    # So map "end_turn" -> END.
    # Map "discovery" -> "discovery" (if we skipped Entry).
    # But Entry node executes FIRST.
    # If Entry node executes and changes phase to "discovery", we want to stop.
    # So lambda returns "end_turn".
    # BUT if Entry node was skipped (returned {}), phase is "discovery".
    # We want to go to "discovery_node".
    
    # We need to know if Entry Node actually DID something.
    # We can check if `questions_asked` is empty and `current_response` is Greeting?
    # This is getting complicated.
    
    # Simple fix:
    # Entry Node returns specific key `__entry_executed`: True?
    # No.
    
    # Let's rely on standard flow:
    # Entry -> Discovery
    # Inside Discovery:
    #    If we just came from Entry (Greeting shown), we shouldn't ask Q1 yet?
    #    Actually Entry Node returns Greeting.
    #    If we go to Discovery Node immediately, it will overwrite Greeting with Q1.
    #    So we MUST STOP after Entry Node if it executed.
    
    # Logic:
    # If phase changed from Entry to Discovery IN THIS TURN -> Stop.
    # Since we can't easily track "in this turn", let's assume:
    # Entry Node sets phase="discovery".
    # Router sees "discovery".
    # It sends to "discovery_node".
    # "discovery_node" generates Q1.
    # So user sees Q1 immediately, missing Greeting?
    # Or Greeting + Q1 joined?
    # That is actually FINE. "Hello! help? + What support?"
    # So we don't need to stop.
    
    # BUT we need to stop after Q1.
    # So Discovery -> END.
    
    # So: 
    # Entry -> Discovery
    # Discovery -> END (if question asked)
    # Discovery -> Recommendation (if done)
    
    # Re-verify Entry logic:
    # Entry sets Greeting as response.
    # Entry sets phase="discovery".
    # Discovery runs.
    # Discovery sees `questions_asked` = [].
    # Discovery sees `input_text`. (Which is "Ask for help" or "Start").
    # It tries to process answer? ("Ask for help" is not valid answer).
    # It likely fails mapping or skips?
    # If it skips processing, it asks Q1.
    # So Response = Q1.
    # Greeting is LOST.
    
    # We want Response = Greeting + Q1.
    # Or just Greeting (which contains Q1 text).
    # Entry config `entry_message` usually includes the first question.
    # So Entry Node setting response is enough.
    # We just need to prevent Discovery Node from overwriting it.
    
    # So Entry Node sets `last_node`="entry".
    # Discovery Node: if `last_node`="entry", return {} (don't run).
    # Then Discovery -> END.
    
    # Next turn:
    # Entry Node skips (phase=discovery).
    # Discovery Node runs (`last_node` missing or different).
    # Processes answer. Gen Q2.
    
    # Implementation: Add `last_agent_step`="entry" in Entry Node.
    
)

def route_entry(state):
    # Entry just initializes. If we are here, we probably want to end turn to show greeting?
    # BUT if we want to skip straightforward to answering, we should go to recommendation.
    # Actually, Entry Node logic above returns "current_response"=Greeting.
    # If we want the bot to greet first, we return END.
    # If the user has already input text (unlikely for entry), we might want to process.
    
    # For now, let's just Show Greeting.
    if state.get("last_agent_step") == "entry":
        return END
    
    # If we are resuming, phase is "recommendation".
    return "recommendation"

conversation_workflow.add_conditional_edges("entry", route_entry)
# Remove discovery routing as we skip it
# conversation_workflow.add_conditional_edges("discovery", route_discovery)
conversation_workflow.add_edge("recommendation", "synthesis")
conversation_workflow.add_edge("synthesis", END)

conversation_graph = conversation_workflow.compile()


# --- Public Interface ---

def run_conversation(input_text: str, existing_state: Optional[Dict] = None, language: str = "en", chat_history: List[str] = []) -> Dict[str, Any]:
    """
    Run the conversation agent with given input.
    """
    if existing_state:
        state = existing_state.copy()
        state["input_text"] = input_text
        state["language"] = language
        state["chat_history"] = chat_history # Update history
        # Clear last step marker for new turn
        if "last_agent_step" in state:
            del state["last_agent_step"]
    else:
        state = get_initial_conversation_state()
        state["input_text"] = input_text
        state["language"] = language
        state["chat_history"] = chat_history
    
    result = conversation_graph.invoke(state)
    return result
