from typing import TypedDict, List, Optional, Any, Dict
from src.schemas import BenefitsAnalysisOutput, CitizenProfile

class BenefitsState(TypedDict):
    """
    State for the Benefits Agent Subgraph.
    """
    input_text: str
    
    # Citizen profile (from eligibility agent or extracted)
    citizen_profile: Optional[CitizenProfile]
    
    # Benefits analysis
    analysis_output: Optional[BenefitsAnalysisOutput]
    
    # Final outputs
    final_markdown_response: Optional[str]
    final_json_response: Optional[Dict[str, Any]]
    
    # Global Preference
    language: str
