import pytest
from unittest.mock import MagicMock, patch
from src.state import AgentState
from src.graph import app
from src.schemas import RouteDecision
from langchain_core.messages import HumanMessage, AIMessage

# Mock the agents processing to return deterministic responses 
# instead of hitting the real LLM which might be slow or unstable (Ollama)
@patch("src.graph.orchestrator_agent.invoke")
@patch("src.graph.policy_agent.invoke")
def test_workflow_orchestrator_routing(mock_policy, mock_orchestrator):
    # Setup Orchestrator to route to POLICY
    mock_orchestrator.return_value = RouteDecision(next_agent="POLICY")
    
    # Setup Policy Agent to return a response
    mock_policy.return_value = AIMessage(content="Policy explained.")
    
    initial_state = {
        "input_text": "Tell me about the zoning policy.",
        "messages": [HumanMessage(content="Tell me about the zoning policy.")]
    }
    
    # Run the graph
    # Depending on how the graph is built, we check valid transitions.
    # Note: app.stream yields events.
    
    events = list(app.stream(initial_state))
    
    # Check if 'policy_node' was visited
    nodes_visited = [list(evt.keys())[0] for evt in events]
    print(f"Nodes visited: {nodes_visited}")
    assert "orchestrator" in nodes_visited
    assert "policy_agent" in nodes_visited

@patch("src.graph.orchestrator_agent.invoke")
def test_workflow_finish(mock_orchestrator):
    # Setup Orchestrator to FINISH immediately
    mock_orchestrator.return_value = RouteDecision(next_agent="FINISH")
    
    initial_state = {
        "input_text": "Goodbye",
        "messages": [HumanMessage(content="Goodbye")]
    }
    
    events = list(app.stream(initial_state))
    nodes_visited = [list(evt.keys())[0] for evt in events]
    
    assert "orchestrator" in nodes_visited
    assert "policy_agent" not in nodes_visited
