from src.tools import retrieve_policy, check_eligibility_rules, find_benefits_database
from langchain_core.documents import Document

def test_retrieve_policy_no_results(mock_retriever, mock_zynd_agent):
    # Setup mock to return empty list
    mock_retriever.invoke.return_value = []
    
    result = retrieve_policy.invoke("some random query")
    assert result == "No specific policy found for this query."
    
    # Verify zynd agent identity was checked (mocked in conftest)
    # Note: 'invoke' on a StructuredTool calls the underlying func.
    # The get_zynd_agent mock should have been called.

def test_retrieve_policy_with_results(mock_retriever, mock_zynd_agent):
    # Setup mock return
    mock_retriever.invoke.return_value = [
        Document(page_content="Policy Content A", metadata={"source": "doc_a"}),
        Document(page_content="Policy Content B", metadata={"source": "doc_b"})
    ]
    
    result = retrieve_policy.invoke("valid query")
    assert "Policy Content A" in result
    assert "Policy Content B" in result
    assert "Source: doc_a" in result

def test_check_eligibility_rules_found(mock_retriever, mock_zynd_agent):
    mock_retriever.invoke.return_value = [Document(page_content="Must be over 18")]
    
    result = check_eligibility_rules.invoke({
        "age": 20, 
        "income": 1000, 
        "location": "NY", 
        "scheme_name": "Test Scheme"
    })
    
    assert "Found the following rules" in result
    assert "Must be over 18" in result

def test_find_benefits_database_found(mock_retriever, mock_zynd_agent):
    mock_retriever.invoke.return_value = [Document(page_content="Free Healthcare Scheme")]
    
    result = find_benefits_database.invoke("poor citizen")
    assert "Free Healthcare Scheme" in result
