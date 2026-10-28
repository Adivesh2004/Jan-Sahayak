# State Management

This document explains how state is managed across the multi-agent system.

## 🎯 State Architecture

The system uses **hierarchical state management** with different state types for each workflow level:

```
AgentState (Main Orchestrator)
    ↓
┌──────────────┬────────────────┬──────────────┬───────────────┐
│ Interpretation│ Eligibility   │  Benefits    │   Advocacy    │
│    State      │    State      │    State     │     State     │
└──────────────┴────────────────┴──────────────┴───────────────┘
```

## 📊 State Types

### 1. Main State: `AgentState`

**File**: [`src/state.py`](file:///c:/Users/bhara/Desktop/Projects/zynd-protocals-application/src/state.py)

Used by the main orchestrator graph to maintain overall conversation context.

```python
class AgentState(TypedDict):
    # Input
    input_text: str
    
    # Routing
    current_intent: Optional[str]  # Which agent to route to
    
    # Conversation History
    messages: Annotated[list[AnyMessage], add_messages]
    
    # Context Data (populated by agents)
    interpreted_policy: Optional[str]
    citizen_profile: Optional[dict]
    
    # Decisions
    is_eligible: Optional[bool]
    eligibility_reason: Optional[str]
    matched_benefits: Optional[List[str]]
    advocacy_plan: Optional[str]
```

#### Key Fields

- **`input_text`**: Current user query
- **`current_intent`**: Routing decision (e.g., "POLICY_INTERPRETER")
- **`messages`**: Full conversation history with `add_messages` reducer
- **Context fields**: Populated by specialized agents for potential cross-agent sharing

#### Special Feature: `add_messages`

The `messages` field uses LangGraph's `add_messages` reducer, which:
- Automatically appends new messages
- Maintains conversation history
- Enables conversation memory with checkpointing

### 2. Interpretation State: `InterpretationState`

**File**: [`src/interpretation_state.py`](file:///c:/Users/bhara/Desktop/Projects/zynd-protocals-application/src/interpretation_state.py)

Used by the Policy Navigator subgraph.

```python
class InterpretationState(TypedDict):
    input_text: str
    
    # Detected intent
    intent: Optional[str]
    
    # Retrieved documents
    retrieved_docs: List[Any]
    
    # Structured analysis
    analysis_output: Optional[PolicyAnalysisOutput]
    
    # Final outputs
    final_markdown_response: Optional[str]
    final_json_response: Optional[Dict[str, Any]]
```

#### Workflow
1. **Input**: `input_text` from user
2. **Intent Detection**: Populates `intent`
3. **RAG Retrieval**: Populates `retrieved_docs`
4. **Extraction**: Populates `analysis_output`
5. **Synthesis**: Populates `final_markdown_response` and `final_json_response`

### 3. Eligibility State: `EligibilityState`

**File**: [`src/eligibility_state.py`](file:///c:/Users/bhara/Desktop/Projects/zynd-protocals-application/src/eligibility_state.py)

Used by the Eligibility Verifier subgraph.

```python
class EligibilityState(TypedDict):
    input_text: str
    
    # Extracted citizen profile
    citizen_profile: Optional[CitizenProfile]
    
    # Analysis output
    analysis_output: Optional[EligibilityAnalysisOutput]
    
    # Final outputs
    final_markdown_response: Optional[str]
    final_json_response: Optional[Dict[str, Any]]
```

#### Workflow
1. **Profile Extraction**: Populates `citizen_profile`
2. **Evaluation**: Populates `analysis_output`
3. **Synthesis**: Populates final responses

### 4. Benefits State: `BenefitsState`

**File**: [`src/benefits_state.py`](file:///c:/Users/bhara/Desktop/Projects/zynd-protocals-application/src/benefits_state.py)

Used by the Benefits Matcher subgraph.

```python
class BenefitsState(TypedDict):
    input_text: str
    
    # Extracted citizen profile
    citizen_profile: Optional[CitizenProfile]
    
    # Analysis output
    analysis_output: Optional[BenefitsAnalysisOutput]
    
    # Final outputs
    final_markdown_response: Optional[str]
    final_json_response: Optional[Dict[str, Any]]
```

### 5. Advocacy State: `AdvocacyState`

**File**: [`src/advocacy_state.py`](file:///c:/Users/bhara/Desktop/Projects/zynd-protocals-application/src/advocacy_state.py)

Used by the Advocacy Agent subgraph.

```python
class AdvocacyState(TypedDict):
    input_text: str
    
    # Selected scheme
    selected_scheme: Optional[str]
    
    # Advocacy analysis
    analysis_output: Optional[AdvocacyAnalysisOutput]
    
    # Final outputs
    final_markdown_response: Optional[str]
    final_json_response: Optional[Dict[str, Any]]
```

## 🔄 State Flow Patterns

### Pattern 1: Main Graph to Subgraph

When the orchestrator routes to a specialized agent:

```python
# In graph.py
def policy_node(state: AgentState):
    # Extract input from main state
    input_text = state.get("input_text", "")
    
    # Invoke subgraph with its own state type
    result = policy_navigator_graph.invoke({
        "input_text": input_text
    })
    
    # Extract response and update main state
    response_text = result.get("final_markdown_response", "")
    return {"messages": [HumanMessage(content=response_text)]}
```

**Key Points**:
- Main state is **not** passed directly to subgraphs
- Only relevant data (`input_text`) is extracted
- Subgraph returns response as a message
- Messages are added to conversation history

### Pattern 2: Within Subgraph

State transitions within a subgraph:

```python
# In policy_navigator.py
def intent_node(state: InterpretationState):
    query = state["input_text"]
    intent = detect_intent(query)
    return {"intent": intent}  # Updates state.intent

def rag_node(state: InterpretationState):
    query = state["input_text"]
    docs = retrieve(query)
    return {"retrieved_docs": docs}  # Updates state.retrieved_docs
```

**Key Points**:
- Each node receives current state
- Returns dict with fields to update
- LangGraph merges updates into state
- Next node receives updated state

## 🧩 State Update Mechanisms

### TypedDict Merge

LangGraph merges node outputs into state:

```python
# Current state
state = {"input_text": "query", "intent": None}

# Node returns
return {"intent": "policy_explanation"}

# Merged state
state = {"input_text": "query", "intent": "policy_explanation"}
```

### Annotated Reducers

Special handling for `messages`:

```python
messages: Annotated[list[AnyMessage], add_messages]
```

The `add_messages` reducer:
- Appends new messages to list
- Prevents duplication
- Maintains order

Example:
```python
# Current state
state = {"messages": [HumanMessage(content="Hi")]}

# Node returns
return {"messages": [AIMessage(content="Hello!")]}

# Merged state (appended, not replaced)
state = {"messages": [
    HumanMessage(content="Hi"),
    AIMessage(content="Hello!")
]}
```

## 💾 State Persistence

### Checkpointing

The main graph uses LangGraph's `MemorySaver`:

```python
from langgraph.checkpoint.memory import MemorySaver

checkpointer = MemorySaver()
app = workflow.compile(checkpointer=checkpointer)
```

### Thread Configuration

Conversations are identified by thread ID:

```python
thread_config = {"configurable": {"thread_id": "1"}}

# State persists across invocations with same thread_id
app.invoke(inputs, config=thread_config)
```

### Session Logs

Additionally, [`main.py`](file:///c:/Users/bhara/Desktop/Projects/zynd-protocals-application/src/main.py) saves session history to JSON:

```python
def save_session_history(thread_id, messages):
    # Saves to logs/session_{thread_id}_{timestamp}.json
    ...
```

## 🔍 State Inspection

### Get Current State

```python
current_state = app.get_state(thread_config)
print(current_state.values)
```

### Get State History

```python
for state in app.get_state_history(thread_config):
    print(state.values)
```

## 🎨 Design Decisions

### Why Separate State Types?

1. **Isolation**: Subgraphs don't need to know about main state structure
2. **Type Safety**: Each workflow has minimal, focused state
3. **Clarity**: Easier to understand what each agent needs
4. **Modularity**: Easy to modify one agent without affecting others

### Why Not Global Shared State?

**Pros of current approach**:
- Clearer boundaries
- Less coupling
- Easier testing
- Reduced complexity

**When shared state might be needed**:
- Cross-agent collaboration (future feature)
- Shared context pool
- Agent-to-agent communication

## 🚀 Future Enhancements

### Planned State Features

1. **Shared Context Pool**
   ```python
   class AgentState(TypedDict):
       # ...existing fields...
       shared_context: Dict[str, Any]  # Available to all agents
   ```

2. **Agent Communication State**
   ```python
   class AgentState(TypedDict):
       # ...
       agent_requests: List[AgentRequest]  # Agents can request help
       agent_responses: List[AgentResponse]
   ```

3. **Human-in-the-Loop State**
   ```python
   class AgentState(TypedDict):
       # ...
       missing_information: List[str]  # What to ask user
       waiting_for_input: bool
   ```

## 📖 Best Practices

### 1. Minimal State
Only include what's necessary for the workflow.

### 2. Immutable Updates
Return new values, don't mutate state in-place.

### 3. Optional Fields
Use `Optional[T]` for fields populated during workflow.

### 4. Type Hints
Always use proper type hints for IDE support.

### 5. Documentation
Document the purpose of each state field.

---

Next: [Data Flow](data-flow.md) to see state in action.
