from typing import TypedDict, Annotated, Sequence, Optional, Dict, Any, List
from langchain_core.messages import BaseMessage
import operator

class AgentState(TypedDict):
    """State for the multi-agent system."""
    messages: Annotated[Sequence[BaseMessage], operator.add]
    current_intent: Optional[str]  # Tracks which agent is active
    input_text: Optional[str]  # User's raw input
    user_profile: Optional[Dict[str, Any]]  # User profile data (age, income, etc.)
    selected_option: Optional[str]  # Which main option user selected
    collected_answers: Optional[Dict[str, Any]]  # All collected user responses
    
    # Context Data
    interpreted_policy: Optional[str]
    citizen_profile: Optional[dict]
    
    # Conversation Agent State (NEW - Gold Standard)
    conversation_state: Optional[Dict[str, Any]]  # Progressive conversation state
    
    # Decisions
    is_eligible: Optional[bool]
    eligibility_reason: Optional[str]
    matched_benefits: Optional[List[str]]
    advocacy_plan: Optional[str]
    
    # Global Preference
    language: Optional[str] = "en"  # Default to English
