from typing import TypedDict, List, Optional, Any, Dict
from src.schemas import EligibilityAnalysisOutput, CitizenProfile

class EligibilityState(TypedDict):
    """
    State for the Eligibility Agent Subgraph.
    """
    input_text: str
    
    # Extracted citizen profile
    citizen_profile: Optional[CitizenProfile]
    
    # Eligibility analysis
    analysis_output: Optional[EligibilityAnalysisOutput]
    
    # Final outputs
    final_markdown_response: Optional[str]
    final_json_response: Optional[Dict[str, Any]]
    
    # Global Preference
    language: str
