# API Reference

Complete reference for schemas, tools, and interfaces in the Zynd Protocols Application.

## 📋 Table of Contents

- [Pydantic Schemas](#pydantic-schemas)
- [State Types](#state-types)
- [Tools](#tools)
- [Agent Interfaces](#agent-interfaces)
- [LLM Configuration](#llm-configuration)

---

## Pydantic Schemas

All schemas are defined in [`src/schemas.py`](file:///c:/Users/bhara/Desktop/Projects/zynd-protocals-application/src/schemas.py)

### RouteDecision

Used by orchestrator to route queries.

```python
class RouteDecision(BaseModel):
    next_agent: Literal[
        "POLICY_INTERPRETER",
        "ELIGIBILITY_VERIFIER",
        "BENEFIT_MATCHER",
        "CITIZEN_ADVOCATE"
    ]
    reason: str  # Brief reason for routing decision
```

**Example**:
```json
{
  "next_agent": "ELIGIBILITY_VERIFIER",
  "reason": "User asking about eligibility for a scheme"
}
```

---

### Policy Schemas

#### PolicyMetadata
```python
class PolicyMetadata(BaseModel):
    policy_name: Optional[str] = None
    issuing_authority: Optional[str] = None
    jurisdiction: Optional[str] = None
```

#### EligibilityRule
```python
class EligibilityRule(BaseModel):
    condition: str  # e.g., "Age > 18"
    is_mandatory: bool = True
    exceptions: Optional[List[str]] = None
```

#### Benefit
```python
class Benefit(BaseModel):
    benefit_type: str  # monetary, service, reservation, etc.
    description: str
    value: Optional[str] = None  # Amount or specific value
```

#### Obligation
```python
class Obligation(BaseModel):
    action: str  # Action required by citizen
    deadline: Optional[str] = None
```

#### RiskAnalysis
```python
class RiskAnalysis(BaseModel):
    ambiguities: List[str] = []
    risk_level: Literal["low", "medium", "high"] = "low"
    missing_info: List[str] = []
```

#### PolicyAnalysisOutput
```python
class PolicyAnalysisOutput(BaseModel):
    metadata: PolicyMetadata
    summary: str
    eligibility_rules: List[EligibilityRule] = []
    benefits: List[Benefit] = []
    obligations: List[Obligation] = []
    risk_analysis: RiskAnalysis
    confidence_score: float  # 0.0 to 1.0
```

**Example**:
```json
{
  "metadata": {
    "policy_name": "PM-KISAN",
    "issuing_authority": "Ministry of Agriculture",
    "jurisdiction": "All of India"
  },
  "summary": "Direct income support for farmers",
  "eligibility_rules": [
    {
      "condition": "Must own agricultural land",
      "is_mandatory": true,
      "exceptions": null
    }
  ],
  "benefits": [
    {
      "benefit_type": "monetary",
      "description": "Annual income support",
      "value": "Rs 6000 per year"
    }
  ],
  "obligations": [],
  "risk_analysis": {
    "ambiguities": [],
    "risk_level": "low",
    "missing_info": []
  },
  "confidence_score": 0.95
}
```

---

### Eligibility Schemas

#### CitizenProfile
```python
class CitizenProfile(BaseModel):
    age: Optional[int] = None
    income: Optional[float] = None
    category: Optional[str] = None  # Category/Caste
    location: Optional[str] = None
    education_level: Optional[str] = None
    employment_status: Optional[str] = None
```

#### EligibilityResult
```python
class EligibilityResult(BaseModel):
    status: Literal["eligible", "not_eligible", "conditional"]
    reasoning: List[str] = []
    failed_conditions: List[str] = []
    exceptions_applied: List[str] = []
```

#### MatchedBenefit
```python
class MatchedBenefit(BaseModel):
    scheme_name: str
    benefit_type: str
    benefit_value: Optional[str] = None
    confidence_score: float
```

#### AppealGuidance
```python
class AppealGuidance(BaseModel):
    is_applicable: bool = False
    reason: Optional[str] = None
    suggested_actions: List[str] = []
```

#### EligibilityAnalysisOutput
```python
class EligibilityAnalysisOutput(BaseModel):
    citizen_profile_summary: CitizenProfile
    eligibility_result: EligibilityResult
    matched_benefits: List[MatchedBenefit] = []
    required_documents: List[str] = []
    next_steps: List[str] = []
    appeal_guidance: AppealGuidance
    risk_level: Literal["low", "medium", "high"] = "low"
    overall_confidence_score: float
```

---

### Benefits Schemas

#### BenefitClaim
```python
class BenefitClaim(BaseModel):
    steps: List[str] = []
    required_documents: List[str] = []
    deadline: Optional[str] = None
    application_mode: Optional[str] = None  # online/offline/hybrid
```

#### DetailedBenefit
```python
class DetailedBenefit(BaseModel):
    scheme_name: str
    benefit_type: str
    benefit_value: Optional[str] = None
    priority_rank: int
    confidence_score: float
    why_you_qualify: List[str] = []
    policy_references: List[str] = []
    how_to_claim: BenefitClaim
```

#### BenefitConflict
```python
class BenefitConflict(BaseModel):
    benefit_a: str
    benefit_b: str
    reason: str
```

#### BenefitsAnalysisOutput
```python
class BenefitsAnalysisOutput(BaseModel):
    citizen_profile_summary: CitizenProfile
    eligible_benefits: List[DetailedBenefit] = []
    conflicts_or_exclusions: List[BenefitConflict] = []
    overall_confidence_score: float
```

---

### Advocacy Schemas

#### ApplicationPath
```python
class ApplicationPath(BaseModel):
    mode: Literal["online", "offline", "hybrid"]
    portal_or_office: str
    deadline: Optional[str] = None
```

#### DocumentStatus
```python
class DocumentStatus(BaseModel):
    ready: List[str] = []
    missing: List[str] = []
    high_risk: List[str] = []  # Documents that often cause rejection
```

#### SubmissionGuidance
```python
class SubmissionGuidance(BaseModel):
    steps: List[str] = []
    common_mistakes: List[str] = []
    validation_checks: List[str] = []
```

#### PostSubmission
```python
class PostSubmission(BaseModel):
    expected_timelines: str
    status_meanings: Dict[str, str] = {}
```

#### AppealSupport
```python
class AppealSupport(BaseModel):
    eligible: bool = False
    reason: Optional[str] = None
    steps: List[str] = []
    escalation_options: List[str] = []
```

#### AdvocacyAnalysisOutput
```python
class AdvocacyAnalysisOutput(BaseModel):
    selected_scheme: str
    application_path: ApplicationPath
    document_status: DocumentStatus
    submission_guidance: SubmissionGuidance
    post_submission: PostSubmission
    appeal_support: AppealSupport
    overall_confidence: float
    citations: List[str] = []
```

---

## State Types

### AgentState
**File**: `src/state.py`

```python
class AgentState(TypedDict):
    input_text: str
    current_intent: Optional[str]
    messages: Annotated[list[AnyMessage], add_messages]
    
    # Context
    interpreted_policy: Optional[str]
    citizen_profile: Optional[dict]
    
    # Decisions
    is_eligible: Optional[bool]
    eligibility_reason: Optional[str]
    matched_benefits: Optional[List[str]]
    advocacy_plan: Optional[str]
```

### InterpretationState
**File**: `src/interpretation_state.py`

```python
class InterpretationState(TypedDict):
    input_text: str
    intent: Optional[str]
    retrieved_docs: List[Any]
    analysis_output: Optional[PolicyAnalysisOutput]
    final_markdown_response: Optional[str]
    final_json_response: Optional[Dict[str, Any]]
```

### EligibilityState
**File**: `src/eligibility_state.py`

```python
class EligibilityState(TypedDict):
    input_text: str
    citizen_profile: Optional[CitizenProfile]
    analysis_output: Optional[EligibilityAnalysisOutput]
    final_markdown_response: Optional[str]
    final_json_response: Optional[Dict[str, Any]]
```

### BenefitsState
**File**: `src/benefits_state.py`

```python
class BenefitsState(TypedDict):
    input_text: str
    citizen_profile: Optional[CitizenProfile]
    analysis_output: Optional[BenefitsAnalysisOutput]
    final_markdown_response: Optional[str]
    final_json_response: Optional[Dict[str, Any]]
```

### AdvocacyState
**File**: `src/advocacy_state.py`

```python
class AdvocacyState(TypedDict):
    input_text: str
    selected_scheme: Optional[str]
    analysis_output: Optional[AdvocacyAnalysisOutput]
    final_markdown_response: Optional[str]
    final_json_response: Optional[Dict[str, Any]]
```

---

## Tools

All tools are defined in [`src/tools.py`](file:///c:/Users/bhara/Desktop/Projects/zynd-protocals-application/src/tools.py)

### retrieve_policy

```python
@tool
def retrieve_policy(query: str) -> str:
    """
    Retrieves relevant policy documents using RAG.
    
    Args:
        query: The policy-related query
        
    Returns:
        Retrieved policy text
    """
```

**Usage**:
```python
result = retrieve_policy.invoke({"query": "PM-KISAN eligibility"})
```

### check_eligibility_rules

```python
@tool
def check_eligibility_rules(scheme_name: str, citizen_data: str) -> str:
    """
    Checks eligibility rules for a specific scheme.
    
    Args:
        scheme_name: Name of the scheme
        citizen_data: Citizen information as string
        
    Returns:
        Eligibility determination
    """
```

### find_benefits_database

```python
@tool
def find_benefits_database(citizen_profile: str) -> str:
    """
    Searches for benefits matching citizen profile.
    
    Args:
        citizen_profile: Profile information
        
    Returns:
        List of matching benefits
    """
```

---

## Agent Interfaces

### Creating an Agent

**File**: `src/agents.py`

```python
def create_agent(system_prompt: str, tools=None):
    """
    Creates an agent with given prompt and tools.
    
    Args:
        system_prompt: System prompt for the agent
        tools: Optional list of tools to bind
        
    Returns:
        Configured agent chain
    """
    if tools:
        return ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("placeholder", "{messages}"),
        ]) | llm.bind_tools(tools)
    else:
        return ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("placeholder", "{messages}"),
        ]) | llm
```

### Agent Instances

```python
# Policy Agent
policy_agent = create_agent(
    policy_system_prompt,
    tools=[retrieve_policy]
)

# Eligibility Agent
eligibility_agent = create_agent(
    eligibility_system_prompt,
    tools=[check_eligibility_rules]
)

# Benefits Agent
benefit_agent = create_agent(
    benefit_system_prompt,
    tools=[find_benefits_database]
)

# Advocacy Agent
advocacy_agent = create_agent(advocacy_system_prompt)

# Orchestrator Agent
orchestrator_agent = ChatPromptTemplate.from_messages([
    ("system", orchestrator_system_prompt),
    ("placeholder", "{messages}"),
]) | llm.with_structured_output(RouteDecision)
```

---

## LLM Configuration

**File**: `src/agents.py`

### Current Configuration (Groq)

```python
from langchain_groq import ChatGroq
import os
from dotenv import load_dotenv

load_dotenv()

llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    temperature=0,
    groq_api_key=os.getenv("GROQ_API_KEY")
)
```

### Alternative Configurations

#### Google Gemini
```python
from langchain_google_genai import ChatGoogleGenerativeAI

llm = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash-exp",
    temperature=0,
    google_api_key=os.getenv("GOOGLE_API_KEY")
)
```

#### Ollama (Local)
```python
from langchain_ollama import ChatOllama

llm = ChatOllama(
    model="llama3.2:3b",
    temperature=0,
    base_url="http://localhost:11434"
)
```

### Structured Output

Convert any LLM to structured output:
```python
structured_llm = llm.with_structured_output(YourPydanticModel)
result = structured_llm.invoke([HumanMessage(content="query")])
# result is an instance of YourPydanticModel
```

---

## Cache Helper API

**File**: `src/cache_helper.py`

### Methods

```python
class CacheHelper:
    @staticmethod
    def hash_query(query: str, context: str = "") -> str:
        """Generate cache key from query and context."""
        
    @staticmethod
    def get_llm_cache(key: str) -> Optional[Any]:
        """Retrieve cached LLM result."""
        
    @staticmethod
    def set_llm_cache(key: str, value: Any) -> None:
        """Store LLM result in cache."""
        
    @staticmethod
    def clear_cache() -> None:
        """Clear all cached results."""
```

### Usage

```python
from src.cache_helper import CacheHelper

# Generate cache key
cache_key = CacheHelper.hash_query(query, context)

# Check cache
cached_result = CacheHelper.get_llm_cache(cache_key)
if cached_result:
    return cached_result

# Compute and cache
result = expensive_llm_call()
CacheHelper.set_llm_cache(cache_key, result)
```

---

## Logger API

**File**: `src/logger.py`

```python
def setup_logger(name: str) -> logging.Logger:
    """
    Creates a configured logger instance.
    
    Args:
        name: Logger name (usually module name)
        
    Returns:
        Configured logger
    """
```

### Usage

```python
from src.logger import setup_logger

logger = setup_logger("MyModule")

logger.debug("Debug message")
logger.info("Info message")
logger.warning("Warning message")
logger.error("Error message")
```

---

## Environment Variables

Required in `.env` file:

```bash
# LLM Provider
GROQ_API_KEY=gsk_...

# Embeddings
GOOGLE_API_KEY=AIza...

# Optional: Tracing
LANGCHAIN_TRACING_V2=true
LANGCHAIN_API_KEY=ls_...
LANGCHAIN_PROJECT=zynd-protocols
```

---

## Graph API

### Main Graph

```python
from src.graph import app

# Invoke
result = app.invoke(
    inputs={"input_text": "query", "messages": [...]},
    config={"configurable": {"thread_id": "123"}}
)

# Stream
for event in app.stream(inputs, config):
    print(event)

# Get current state
state = app.get_state(config)
print(state.values)

# Get state history
for historical_state in app.get_state_history(config):
    print(historical_state.values)
```

---

This completes the API reference. For usage examples, see [Data Flow](data-flow.md).
