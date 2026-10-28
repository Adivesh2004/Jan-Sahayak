from typing import Annotated, Literal
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from langchain_core.messages import HumanMessage
from src.state import AgentState
from src.agents import (
    orchestrator_agent, policy_agent, eligibility_agent, 
    benefit_agent, advocacy_agent
)
from src.tools import retrieve_policy, check_eligibility_rules, find_benefits_database

from src.config import get_zynd_agent
from src.logger import setup_logger

logger = setup_logger("Graph")

# --- Nodes ---

def orchestrator_node(state: AgentState):
    logger.info("Orchestrator processing...")
    try:
        # Check if intent is already set (from UI option selection)
        if state.get("current_intent") and state.get("selected_option"):
            logger.info(f"Intent already set by UI: {state['current_intent']}")
            # Skip orchestration, return existing intent
            return {"current_intent": state["current_intent"]}
        
        # Initialize Orchestrator Identity
        zynd_agent = get_zynd_agent("ORCHESTRATOR")
        if zynd_agent:
            print(f"\n[Node: Orchestrator] Identity Active: {zynd_agent.agent_config.identity_credential_path}")

        messages = state.get("messages", [])
        # If no messages, use input_text
        if not messages and state.get("input_text"):
            messages = [HumanMessage(content=state["input_text"])]
            
        language = state.get("language", "en")
        
        # Pass language to agent for prompt formatting
        decision = orchestrator_agent.invoke({"messages": messages, "language": language})
        return {"current_intent": decision.next_agent}
    except Exception as e:
        logger.error(f"Orchestrator Error: {e}")
        return {"current_intent": "__end__"} # Safely end if orchestrator fails

from src.policy_navigator import policy_navigator_graph

def policy_node(state: AgentState):
    logger.info("Transferring to Policy Navigator...")
    try:
        # Map AgentState to InterpretationState
        # Using the last human message or input_text as input
        input_text = state.get("input_text", "")
        if state.get("messages"):
             # Get last user message
             for msg in reversed(state["messages"]):
                 if isinstance(msg, HumanMessage):
                     input_text = msg.content
                     break
        
        # Enrich with user profile if available
        user_profile = state.get("user_profile")
        if user_profile:
            logger.info(f"Policy Navigator using user profile: {user_profile}")
        
        # Invoke Subgraph
        language = state.get("language", "en")
        result = policy_navigator_graph.invoke({"input_text": input_text, "language": language})
        
        # Extract response
        response_text = result.get("final_markdown_response", "No response generated.")
        
        return {"messages": [HumanMessage(content=response_text)]}
    except Exception as e:
        logger.error(f"Policy Navigator Error: {e}")
        return {"messages": [HumanMessage(content="I encountered an error navigating the policy.")]}

from src.eligibility_verification import eligibility_graph

def eligibility_node(state: AgentState):
    logger.info("Transferring to Eligibility Agent...")
    try:
        input_text = state.get("input_text", "")
        if state.get("messages"):
             for msg in reversed(state["messages"]):
                 if isinstance(msg, HumanMessage):
                     input_text = msg.content
                     break
        
        # Enrich with user profile if available
        user_profile = state.get("user_profile")
        if user_profile:
            logger.info(f"Eligibility Agent using user profile: {user_profile}")
        
        language = state.get("language", "en")
        result = eligibility_graph.invoke({
            "input_text": input_text, 
            "citizen_profile": user_profile,  # Pass profile if available
            "language": language
        })
        response_text = result.get("final_markdown_response", "No response generated.")
        
        return {"messages": [HumanMessage(content=response_text)]}
    except Exception as e:
        logger.error(f"Eligibility Agent Error: {e}")
        return {"messages": [HumanMessage(content="I encountered an error checking eligibility.")]}

from src.benefits_matching import benefits_graph

def benefit_node(state: AgentState):
    logger.info("Transferring to Benefits Agent...")
    try:
        input_text = state.get("input_text", "")
        if state.get("messages"):
             for msg in reversed(state["messages"]):
                 if isinstance(msg, HumanMessage):
                     input_text = msg.content
                     break
        
        # Enrich with user profile if available
        user_profile = state.get("user_profile")
        if user_profile:
            logger.info(f"Benefits Agent using user profile: {user_profile}")
        
        language = state.get("language", "en")
        result = benefits_graph.invoke({
            "input_text": input_text, 
            "citizen_profile": user_profile,
            "language": language
        })
        response_text = result.get("final_markdown_response", "No response generated.")
        
        return {"messages": [HumanMessage(content=response_text)]}
    except Exception as e:
        logger.error(f"Benefits Agent Error: {e}")
        return {"messages": [HumanMessage(content="I encountered an error finding benefits.")]}

from src.advocacy_agent import advocacy_graph
from src.conversation_agent import conversation_graph, run_conversation

def conversation_node(state: AgentState):
    """Life-first conversational discovery flow"""
    logger.info("Transferring to Conversation Agent...")
    try:
        input_text = state.get("input_text", "")
        if state.get("messages"):
            for msg in reversed(state["messages"]):
                if isinstance(msg, HumanMessage):
                    input_text = msg.content
                    break
        
        # Get existing conversation state if available
        existing_state = state.get("conversation_state")
        
        # Prepare chat history from messages
        messages = state.get("messages", [])
        chat_history = []
        for msg in messages:
            role = "User" if isinstance(msg, HumanMessage) else "Sahayak"
            content = msg.content
            chat_history.append(f"{role}: {content}")
        
        language = state.get("language", "en")
        # Pass chat_history to run_conversation
        result = run_conversation(input_text, existing_state, language=language, chat_history=chat_history)
        response_text = result.get("final_markdown_response")
        if not response_text:
            response_text = result.get("current_response", "How can I help you today?")
        
        return {
            "messages": [HumanMessage(content=response_text)],
            "conversation_state": result
        }
    except Exception as e:
        logger.error(f"Conversation Agent Error: {e}")
        return {"messages": [HumanMessage(content="I'm here to help. What kind of support are you looking for?")]}

def advocacy_node(state: AgentState):
    logger.info("Transferring to Advocacy Agent...")
    try:
        input_text = state.get("input_text", "")
        if state.get("messages"):
             for msg in reversed(state["messages"]):
                 if isinstance(msg, HumanMessage):
                     input_text = msg.content
                     break
        
        # Enrich with user profile if available
        user_profile = state.get("user_profile")
        if user_profile:
            logger.info(f"Advocacy Agent using user profile: {user_profile}")
        
        language = state.get("language", "en")
        result = advocacy_graph.invoke({"input_text": input_text, "language": language})
        response_text = result.get("final_markdown_response", "No response generated.")
        
        return {"messages": [HumanMessage(content=response_text)]}
    except Exception as e:
        logger.error(f"Advocacy Agent Error: {e}")
        return {"messages": [HumanMessage(content="I encountered an error generating advocacy guidance.")]}

# --- Graph ---

workflow = StateGraph(AgentState)

workflow.add_node("orchestrator", orchestrator_node)
workflow.add_node("conversation_agent", conversation_node)
workflow.add_node("policy_agent", policy_node)
workflow.add_node("eligibility_agent", eligibility_node)
workflow.add_node("benefit_agent", benefit_node)
workflow.add_node("advocacy_agent", advocacy_node)

# Tool Node (Shared)
tools = [retrieve_policy, check_eligibility_rules, find_benefits_database]
tool_node = ToolNode(tools)
workflow.add_node("tools", tool_node)

# --- Edges ---

def route_orchestrator(state: AgentState) -> Literal["conversation_agent", "policy_agent", "eligibility_agent", "benefit_agent", "advocacy_agent", "__end__"]:
    intent = state.get("current_intent")
    if intent == "CONVERSATION_DISCOVERY":
        return "conversation_agent"
    elif intent == "POLICY_INTERPRETER":
        return "policy_agent"
    elif intent == "ELIGIBILITY_VERIFIER":
        return "eligibility_agent"
    elif intent == "BENEFIT_MATCHER":
        return "benefit_agent"
    elif intent == "CITIZEN_ADVOCATE":
        return "advocacy_agent"
    else:
        return "__end__"

workflow.set_entry_point("orchestrator")
workflow.add_conditional_edges("orchestrator", route_orchestrator)

def route_agent_tools(state: AgentState) -> Literal["tools", "__end__"]:
    last_message = state["messages"][-1]
    if hasattr(last_message, "tool_calls") and len(last_message.tool_calls) > 0:
        return "tools"
    return "__end__"

# Connect agents to tools and back
for agent_name in ["conversation_agent", "policy_agent", "eligibility_agent", "benefit_agent", "advocacy_agent"]:
    workflow.add_conditional_edges(agent_name, route_agent_tools)
    
# Tools go back to the agent that called them
# NOTE: This simple graph assumes the last agent called the tool. 
# LangGraph ToolNode execution updates state["messages"], so we just need to route back to the active agent.
# But "tools" node output doesn't know who called it. 
# We need to use valid routing logic. 
# For simplicity, we can route based on `current_intent` preserved in state.

def route_tools_back(state: AgentState):
    intent = state.get("current_intent")
    if intent == "CONVERSATION_DISCOVERY":
        return "conversation_agent"
    elif intent == "POLICY_INTERPRETER":
        return "policy_agent"
    elif intent == "ELIGIBILITY_VERIFIER":
        return "eligibility_agent"
    elif intent == "BENEFIT_MATCHER":
        return "benefit_agent"
    elif intent == "CITIZEN_ADVOCATE":
        return "advocacy_agent"
    return "__end__"

workflow.add_conditional_edges("tools", route_tools_back)

import sqlite3
try:
    from langgraph.checkpoint.sqlite import SqliteSaver
    # Ensure the database connection is thread-safe for Flask
    # check_same_thread=False is needed because Flask uses multiple threads
    conn = sqlite3.connect("jan_sahayak.db", check_same_thread=False)
    checkpointer = SqliteSaver(conn)
    logger.info("Using SqliteSaver for persistent chat history.")
except ImportError:
    logger.warning("langgraph-checkpoint-sqlite not found. Falling back to MemorySaver (History will not persist).")
    from langgraph.checkpoint.memory import MemorySaver
    checkpointer = MemorySaver()

app = workflow.compile(checkpointer=checkpointer)
