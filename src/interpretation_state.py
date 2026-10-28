from typing import TypedDict, List, Optional, Any, Dict
from src.schemas import PolicyAnalysisOutput

class InterpretationState(TypedDict):
    """
    State for the Policy Navigator Subgraph.
    """
    input_text: str
    
    # Internal Processing Logic
    intent: Optional[str]
    domain: Optional[str]
    
    # RAG
    retrieved_docs: List[Any]
    
    # Extracted Date
    analysis_output: Optional[PolicyAnalysisOutput]
    
    # Final Synthesis
    final_markdown_response: Optional[str]
    final_json_response: Optional[Dict[str, Any]]
    
    # Global Preference
    language: str
