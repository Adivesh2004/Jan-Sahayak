from src.graph import app
from src.state import AgentState

def test_graph_structure():
    # Verify nodes exist in the graph
    nodes = app.get_graph(xray=True).nodes
    assert "orchestrator" in nodes
    assert "policy_agent" in nodes
    assert "eligibility_agent" in nodes
    assert "benefit_agent" in nodes
    assert "advocacy_agent" in nodes

def test_graph_compile():
    # Ensure the graph compiles without error (it's already compiled on import)
    assert app is not None
