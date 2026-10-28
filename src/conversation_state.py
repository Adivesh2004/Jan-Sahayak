"""
Conversation State for Life-First Citizen Discovery Flow
Manages progressive citizen profile building through conversational interaction
"""
from typing import TypedDict, List, Optional, Dict, Any
from langgraph.graph import add_messages


class CitizenDiscoveryProfile(TypedDict, total=False):
    """Progressive citizen profile built through conversation"""
    # Basic Demographics
    age_range: str  # "18-25", "26-40", "41-60", "60+"
    actual_age: Optional[int]
    
    # Employment & Income
    employment_status: str  # "employed", "self-employed", "unemployed", "student", "retired"
    income_bracket: str  # "below_1_lakh", "1_to_2.5_lakh", "2.5_to_5_lakh", "above_5_lakh"
    annual_income: Optional[float]
    
    # Family
    family_size: int
    has_dependents: bool
    has_children_in_school: bool
    has_senior_citizens: bool
    
    # Location
    state: str
    district: Optional[str]
    is_rural: bool
    
    # Special Conditions
    has_disability: bool
    disability_type: Optional[str]
    is_woman: bool
    is_minority: bool
    social_category: Optional[str]  # SC, ST, OBC, General
    
    # Needs & Interests
    primary_need: str  # "healthcare", "education", "housing", "income", "employment", "other"
    secondary_needs: List[str]
    specific_situation: Optional[str]


class ConversationState(TypedDict, total=False):
    """State for the conversational discovery flow"""
    # Input
    input_text: str
    
    # Conversation Management
    conversation_phase: str  # "entry", "discovery", "profiling", "recommendation", "application", "complete"
    current_question_id: str
    questions_asked: List[str]
    questions_remaining: List[str]
    
    # Profile Building (Progressive)
    citizen_profile: CitizenDiscoveryProfile
    profile_completeness: float  # 0.0 to 1.0
    
    # Discovered Needs
    discovered_needs: List[str]
    priority_need: str
    
    # Trust & Engagement
    session_trust_level: float  # 0.0 to 1.0, increases as user shares more
    privacy_consent_given: bool
    
    # RAG Context
    retrieved_policies: List[str]
    retrieved_benefits: List[str]
    
    # Response
    current_response: str
    final_markdown_response: str
    
    # Recommendations (when ready)
    matched_schemes: List[Dict[str, Any]]
    recommendation_confidence: float

    # Global Preference
    language: str
    
    # Chat History (Context)
    chat_history: List[str]


# Phase definitions for conversation flow
CONVERSATION_PHASES = {
    "entry": {
        "description": "Initial greeting and needs discovery",
        "next_phases": ["discovery"],
        "required_fields": []
    },
    "discovery": {
        "description": "Understanding citizen's life situation",
        "next_phases": ["profiling"],
        "required_fields": ["primary_need"]
    },
    "profiling": {
        "description": "Collecting demographic and eligibility information",
        "next_phases": ["recommendation"],
        "required_fields": ["age_range", "employment_status", "income_bracket", "state"]
    },
    "recommendation": {
        "description": "Showing matched schemes with explanations",
        "next_phases": ["application", "complete"],
        "required_fields": []
    },
    "application": {
        "description": "Guiding through application process",
        "next_phases": ["tracking", "complete"],
        "required_fields": []
    },
    "tracking": {
        "description": "Post-application status tracking",
        "next_phases": ["complete"],
        "required_fields": []
    },
    "complete": {
        "description": "Session complete with ongoing relationship setup",
        "next_phases": [],
        "required_fields": []
    }
}


def get_initial_conversation_state() -> ConversationState:
    """Create initial conversation state for new session"""
    return ConversationState(
        input_text="",
        conversation_phase="entry",
        current_question_id="",
        questions_asked=[],
        questions_remaining=[],
        citizen_profile=CitizenDiscoveryProfile(),
        profile_completeness=0.0,
        discovered_needs=[],
        priority_need="",
        session_trust_level=0.0,
        privacy_consent_given=False,
        retrieved_policies=[],
        retrieved_benefits=[],
        current_response="",
        final_markdown_response="",
        matched_schemes=[],
        recommendation_confidence=0.0,
        language="en"
    )
