from typing import TypedDict, List, Optional, Any, Dict
from src.schemas import AdvocacyAnalysisOutput

class AdvocacyState(TypedDict):
    """
    State for the Advocacy Agent Subgraph.
    """
    input_text: str
    
    # Selected scheme (can be extracted from query or passed from benefits agent)
    selected_scheme: Optional[str]
    
    # Advocacy analysis
    analysis_output: Optional[AdvocacyAnalysisOutput]
    
    # Final outputs
    final_markdown_response: Optional[str]
    final_json_response: Optional[Dict[str, Any]]
    
    # Global Preference
    language: str
