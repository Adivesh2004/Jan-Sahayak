from pydantic import BaseModel, Field
from typing import List, Optional, Literal, Dict, Union

class RouteDecision(BaseModel):
    next_agent: Literal["CONVERSATION_DISCOVERY", "POLICY_INTERPRETER", "ELIGIBILITY_VERIFIER", "BENEFIT_MATCHER", "CITIZEN_ADVOCATE"] = Field(
        description="The next agent to route the request to based on user intent."
    )
    reason: str = Field(description="Brief reason for the routing decision.")

# --- Policy Navigator Schemas ---

class PolicyMetadata(BaseModel):
    policy_name: Optional[str] = Field(None, description="Name of the policy")
    issuing_authority: Optional[str] = Field(None, description="Authority issuing the policy")
    jurisdiction: Optional[str] = Field(None, description="Applies to which region/group")

class EligibilityRule(BaseModel):
    condition: str = Field(..., description="The condition required (e.g., 'Age > 18')")
    is_mandatory: bool = Field(True, description="Is this condition mandatory?")
    exceptions: Optional[List[str]] = Field(None, description="Any exceptions to this rule")

class Benefit(BaseModel):
    benefit_type: str = Field(..., description="Type: monetary, service, reservation, etc.")
    description: str = Field(..., description="Description of the benefit")
    value: Optional[str] = Field(None, description="Amount or specific value if applicable")

class Obligation(BaseModel):
    action: str = Field(..., description="Action required by the citizen")
    deadline: Optional[str] = Field(None, description="Deadline for the action")

class RiskAnalysis(BaseModel):
    ambiguities: List[str] = Field(default_factory=list, description="Vague or unclear terms found")
    risk_level: Literal["low", "medium", "high"] = Field("low", description="Overall risk level of misinterpretation")
    missing_info: List[str] = Field(default_factory=list, description="Critical information missing from the text")

class PolicyAnalysisOutput(BaseModel):
    metadata: PolicyMetadata
    summary: str = Field(..., description="High-level summary of the policy")
    eligibility_rules: List[EligibilityRule] = Field(default_factory=list)
    benefits: List[Benefit] = Field(default_factory=list)
    obligations: List[Obligation] = Field(default_factory=list)
    risk_analysis: RiskAnalysis
    confidence_score: float = Field(..., description="Confidence score between 0.0 and 1.0")

# --- Eligibility Agent Schemas ---

# ENHANCED: Support both precise values and conversational ranges
class CitizenProfile(BaseModel):
    age: Optional[Union[int, str]] = Field(None, description="Age of the citizen (can be int or range like '26-40')")
    income: Optional[Union[float, str]] = Field(None, description="Annual income (can be number or range like 'Below 2.5 lakh')")
    category: Optional[str] = Field(None, description="Category/Caste if applicable")
    location: Optional[str] = Field(None, description="Residency location")
    education_level: Optional[str] = Field(None, description="Education level")
    employment_status: Optional[str] = Field(None, description="Employment status")
    family_size: Optional[Union[int, str]] = Field(None, description="Number of family members")
    special_conditions: Optional[List[str]] = Field(None, description="Special conditions (disability, widow, senior, etc.)")

# ENHANCED: Three-tier eligibility status (supports uppercase from LLM)
class EligibilityResult(BaseModel):
    status: Literal["eligible", "not_eligible", "conditional", "possibly_eligible", 
                    "ELIGIBLE", "NOT_ELIGIBLE", "CONDITIONAL", "POSSIBLY_ELIGIBLE"] = Field(
        ..., description="Eligibility status (three-tier: eligible/possibly_eligible/not_eligible)"
    )
    reasoning: List[str] = Field(default_factory=list, description="Reasons for the decision")
    failed_conditions: List[str] = Field(default_factory=list, description="Conditions that were not met")
    exceptions_applied: List[str] = Field(default_factory=list, description="Any exceptions that were applied")

class MatchedBenefit(BaseModel):
    scheme_name: str = Field(..., description="Name of the scheme")
    benefit_type: str = Field(..., description="Type of benefit")
    benefit_value: Optional[str] = Field(None, description="Value of the benefit")
    confidence_score: float = Field(..., description="Confidence in this match")

class AppealGuidance(BaseModel):
    is_applicable: bool = Field(False, description="Can the user appeal?")
    reason: Optional[str] = Field(None, description="Reason for appeal possibility")
    suggested_actions: List[str] = Field(default_factory=list)

class EligibilityAnalysisOutput(BaseModel):
    citizen_profile_summary: CitizenProfile
    eligibility_result: EligibilityResult
    matched_benefits: List[MatchedBenefit] = Field(default_factory=list)
    required_documents: List[str] = Field(default_factory=list)
    next_steps: List[str] = Field(default_factory=list)
    appeal_guidance: AppealGuidance
    risk_level: Literal["low", "medium", "high"] = Field("low")
    overall_confidence_score: float = Field(..., description="Overall confidence")

# --- Benefits Agent Schemas ---

class BenefitClaim(BaseModel):
    steps: List[str] = Field(default_factory=list, description="Steps to claim")
    required_documents: List[str] = Field(default_factory=list)
    deadline: Optional[str] = Field(None, description="Deadline to apply")
    application_mode: Optional[str] = Field(None, description="online/offline/hybrid")

class DetailedBenefit(BaseModel):
    scheme_name: str = Field(..., description="Name of the scheme")
    benefit_type: str = Field(..., description="Type of benefit")
    benefit_value: Optional[str] = Field(None, description="Value")
    priority_rank: int = Field(..., description="Priority ranking")
    confidence_score: float = Field(..., description="Confidence score")
    why_you_qualify: List[str] = Field(default_factory=list)
    policy_references: List[str] = Field(default_factory=list)
    how_to_claim: BenefitClaim

class BenefitConflict(BaseModel):
    benefit_a: str
    benefit_b: str
    reason: str

class BenefitsAnalysisOutput(BaseModel):
    citizen_profile_summary: CitizenProfile
    eligible_benefits: List[DetailedBenefit] = Field(default_factory=list)
    conflicts_or_exclusions: List[BenefitConflict] = Field(default_factory=list)
    overall_confidence_score: float = Field(..., description="Overall confidence")

# --- Advocacy Agent Schemas ---

class ApplicationPath(BaseModel):
    mode: Literal["online", "offline", "hybrid"] = Field(..., description="Application mode")
    portal_or_office: str = Field(..., description="Where to apply")
    deadline: Optional[str] = Field(None, description="Application deadline")

class DocumentStatus(BaseModel):
    ready: List[str] = Field(default_factory=list, description="Documents the citizen has")
    missing: List[str] = Field(default_factory=list, description="Documents needed")
    high_risk: List[str] = Field(default_factory=list, description="Documents that often cause rejection")

class SubmissionGuidance(BaseModel):
    steps: List[str] = Field(default_factory=list, description="Step-by-step instructions")
    common_mistakes: List[str] = Field(default_factory=list, description="What to avoid")
    validation_checks: List[str] = Field(default_factory=list, description="Pre-submission checks")

class PostSubmission(BaseModel):
    expected_timelines: str = Field(..., description="How long processing takes")
    status_meanings: Dict[str, str] = Field(default_factory=dict, description="What each status means")

class AppealSupport(BaseModel):
    eligible: bool = Field(False, description="Can the citizen appeal?")
    reason: Optional[str] = Field(None, description="Why appeal is/isn't possible")
    steps: List[str] = Field(default_factory=list, description="Appeal steps")
    escalation_options: List[str] = Field(default_factory=list, description="Who to contact for help")

class AdvocacyAnalysisOutput(BaseModel):
    selected_scheme: str = Field(..., description="The scheme being applied to")
    application_path: ApplicationPath
    document_status: DocumentStatus
    submission_guidance: SubmissionGuidance
    post_submission: PostSubmission
    appeal_support: AppealSupport
    overall_confidence: float = Field(..., description="Confidence in this guidance")
    citations: List[str] = Field(default_factory=list, description="Policy references")

# --- Gold Standard: Trust-Backed Recommendation Schemas ---

class EscalationOption(BaseModel):
    """Escalation contact for appeals and help"""
    type: Literal["ngo", "legal_aid", "human_advocate", "government_helpline"] = Field(..., description="Type of escalation")
    name: str = Field(..., description="Name of organization or contact")
    contact: Optional[str] = Field(None, description="Phone, email, or URL")
    description: str = Field(..., description="What help they provide")

class TrustBackedRecommendation(BaseModel):
    """Ranked benefit recommendation with confidence and reasoning"""
    scheme_name: str = Field(..., description="Name of the scheme")
    priority: Literal["high", "secondary", "future"] = Field(..., description="Priority ranking")
    priority_reason: str = Field(..., description="Why this priority was assigned")
    confidence_score: float = Field(..., description="Confidence in this recommendation (0-1)")
    why_recommended: str = Field(..., description="Plain-language explanation of why citizen qualifies")
    what_you_get: str = Field(..., description="What benefit the citizen will receive")
    action_urgency: Literal["immediate", "within_month", "when_ready"] = Field("when_ready", description="How urgently to act")
    next_step: str = Field(..., description="Single immediate next step to take")

class RecommendationSet(BaseModel):
    """Complete set of recommendations for a citizen"""
    high_priority: List[TrustBackedRecommendation] = Field(default_factory=list, description="Immediate action benefits")
    secondary: List[TrustBackedRecommendation] = Field(default_factory=list, description="Worth pursuing benefits")
    future: List[TrustBackedRecommendation] = Field(default_factory=list, description="Keep in mind for later")
    recommended_order: List[str] = Field(default_factory=list, description="Suggested order to apply")
    recommendation_reasoning: str = Field(..., description="Overall strategy explanation")

# --- Gold Standard: Enhanced Appeals & Rejection Handling ---

class RejectionExplanation(BaseModel):
    """Plain-language rejection explanation"""
    rejection_reason_official: str = Field(..., description="Official reason from authority")
    rejection_reason_plain: str = Field(..., description="What this means in simple words")
    is_correctable: bool = Field(False, description="Can this be fixed and resubmitted?")
    correction_deadline: Optional[str] = Field(None, description="Deadline to correct, if any")

class CorrectionSuggestion(BaseModel):
    """Specific correction to fix rejection"""
    issue: str = Field(..., description="What went wrong")
    how_to_fix: str = Field(..., description="Step-by-step fix")
    documents_needed: List[str] = Field(default_factory=list, description="Documents to gather")
    estimated_time: str = Field("1-2 weeks", description="How long it takes")

class EnhancedAppealSupport(BaseModel):
    """Comprehensive appeal and rejection handling"""
    rejection_explanation: RejectionExplanation
    corrections: List[CorrectionSuggestion] = Field(default_factory=list)
    alternative_schemes: List[TrustBackedRecommendation] = Field(default_factory=list, description="Other schemes to try")
    appeal_possible: bool = Field(False, description="Can formal appeal be filed?")
    appeal_steps: List[str] = Field(default_factory=list, description="How to appeal")
    appeal_deadline: Optional[str] = Field(None, description="Deadline for appeal")
    escalation_options: List[EscalationOption] = Field(default_factory=list, description="Who can help")

# --- Gold Standard: Ongoing Citizen Relationship ---

class ApplicationStatus(BaseModel):
    """Status of a submitted application"""
    scheme_name: str
    application_id: Optional[str] = Field(None)
    current_status: Literal["submitted", "under_review", "documents_requested", "approved", "rejected", "pending_disbursement", "completed"] = Field("submitted")
    status_since: str = Field(..., description="Date of current status")
    next_expected_update: Optional[str] = Field(None, description="When to check again")
    action_required: Optional[str] = Field(None, description="If citizen needs to do something")

class EligibilityChange(BaseModel):
    """Notification about eligibility changes"""
    scheme_name: str
    change_type: Literal["newly_eligible", "deadline_approaching", "rules_changed", "annual_recheck"]
    message: str
    action_deadline: Optional[str] = Field(None)

class OngoingRelationship(BaseModel):
    """Post-application relationship and tracking"""
    citizen_id: Optional[str] = Field(None, description="Anonymized citizen identifier")
    tracked_applications: List[ApplicationStatus] = Field(default_factory=list)
    eligibility_updates: List[EligibilityChange] = Field(default_factory=list)
    next_recheck_date: Optional[str] = Field(None, description="When to recheck all eligibility")
    annual_summary: Optional[str] = Field(None, description="Annual benefit summary for citizen")

# --- Eligibility Three-Tier Status ---

class EligibilityThreeTier(BaseModel):
    """Three-tier eligibility status with explanation"""
    status: Literal["eligible", "possibly_eligible", "not_eligible"] = Field(..., description="Eligibility tier")
    status_emoji: str = Field(..., description="Visual indicator: ✅, ⚠️, or ❌")
    headline: str = Field(..., description="Single-line summary")
    explanation: str = Field(..., description="Why this status was determined")
    missing_for_eligible: List[str] = Field(default_factory=list, description="What's needed to become fully eligible")
    confidence: float = Field(..., description="Confidence in this assessment")

