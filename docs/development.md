# Development Guide

This guide helps developers understand, extend, and contribute to the Zynd Protocols Application.

## 🎯 Development Setup

### Prerequisites
- Python 3.10+
- Git
- Virtual environment tool
- Code editor (VS Code recommended)

### Initial Setup
```bash
# Clone and setup
git clone <repository-url>
cd zynd-protocals-application
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your API keys
```

### Recommended VS Code Extensions
- Python (Microsoft)
- Pylance
- Python Debugger
- LangChain Support (if available)

## 📁 Project Structure

```
zynd-protocals-application/
├── src/                          # Source code
│   ├── main.py                   # CLI entry point
│   ├── streamlit_app.py          # Web UI entry point
│   ├── graph.py                  # Main orchestrator graph
│   ├── agents.py                 # Agent configurations
│   ├── state.py                  # Main state
│   ├── schemas.py                # Pydantic models
│   │
│   ├── policy_navigator.py       # Policy agent subgraph
│   ├── eligibility_verification.py
│   ├── benefits_matching.py
│   ├── advocacy_agent.py
│   │
│   ├── *_state.py                # State definitions for each agent
│   │
│   ├── rag.py                    # RAG setup
│   ├── rag_agent.py              # Agentic RAG
│   ├── tools.py                  # Shared tools
│   ├── prompts.py                # System prompts
│   │
│   ├── config.py                 # Configuration
│   ├── logger.py                 # Logging
│   ├── cache_helper.py           # Caching
│   └── langsmith_config.py       # Tracing
│
├── tests/                        # Test suite
│   ├── unit/                     # Unit tests
│   ├── integration/              # Integration tests
│   └── conftest.py               # Test configuration
│
├── docs/                         # Documentation
├── chroma_db/                    # Vector database
├── logs/                         # Application logs
├── agent_desc_md/                # Agent descriptions
└── requirements.txt              # Dependencies
```

## 🔨 Common Development Tasks

### 1. Adding a New Agent

#### Step 1: Create State Definition
Create `src/new_agent_state.py`:
```python
from typing import TypedDict, Optional, Dict, Any

class NewAgentState(TypedDict):
    input_text: str
    # Add agent-specific fields
    analysis_output: Optional[Any]
    final_markdown_response: Optional[str]
    final_json_response: Optional[Dict[str, Any]]
```

#### Step 2: Define Schemas
Add to `src/schemas.py`:
```python
from pydantic import BaseModel, Field

class NewAgentOutput(BaseModel):
    result: str = Field(..., description="Result description")
    confidence: float = Field(..., description="Confidence score")
```

#### Step 3: Create Agent Subgraph
Create `src/new_agent.py`:
```python
from langgraph.graph import StateGraph, END
from src.new_agent_state import NewAgentState
from src.schemas import NewAgentOutput
from src.agents import llm
from src.logger import setup_logger

logger = setup_logger("NewAgent")

def analysis_node(state: NewAgentState):
    logger.info("Analyzing...")
    # Agent logic here
    structured_llm = llm.with_structured_output(NewAgentOutput)
    result = structured_llm.invoke([...])
    return {"analysis_output": result}

def synthesis_node(state: NewAgentState):
    logger.info("Synthesizing...")
    # Generate user response
    return {"final_markdown_response": "..."}

def build_new_agent_graph():
    workflow = StateGraph(NewAgentState)
    
    workflow.add_node("analysis", analysis_node)
    workflow.add_node("synthesis", synthesis_node)
    
    workflow.set_entry_point("analysis")
    workflow.add_edge("analysis", "synthesis")
    workflow.add_edge("synthesis", END)
    
    return workflow.compile()

new_agent_graph = build_new_agent_graph()
```

#### Step 4: Integrate into Main Graph
Edit `src/graph.py`:

```python
# Import
from src.new_agent import new_agent_graph

# Add node
def new_agent_node(state: AgentState):
    logger.info("Transferring to New Agent...")
    try:
        input_text = state.get("input_text", "")
        result = new_agent_graph.invoke({"input_text": input_text})
        response_text = result.get("final_markdown_response", "")
        return {"messages": [HumanMessage(content=response_text)]}
    except Exception as e:
        logger.error(f"New Agent Error: {e}")
        return {"messages": [HumanMessage(content="Error occurred.")]}

# Register node
workflow.add_node("new_agent", new_agent_node)

# Update routing
def route_orchestrator(state: AgentState):
    intent = state.get("current_intent")
    if intent == "NEW_AGENT_INTENT":
        return "new_agent"
    # ... existing routes ...
```

#### Step 5: Update Orchestrator Prompt
Edit `src/prompts.py`:
```python
ORCHESTRATOR_SYSTEM_PROMPT = """
You are an orchestrator agent...

Available agents:
...
- NEW_AGENT_INTENT: When user needs [specific capability]
"""
```

#### Step 6: Add to Schema
Edit `src/schemas.py`:
```python
class RouteDecision(BaseModel):
    next_agent: Literal[
        "POLICY_INTERPRETER",
        "ELIGIBILITY_VERIFIER",
        "BENEFIT_MATCHER",
        "CITIZEN_ADVOCATE",
        "NEW_AGENT_INTENT"  # Add new intent
    ] = Field(...)
```

### 2. Adding a New Tool

Create a tool in `src/tools.py`:
```python
from langchain_core.tools import tool

@tool
def new_tool_name(query: str) -> str:
    """
    Description of what this tool does.
    
    Args:
        query: The input query
        
    Returns:
        Result string
    """
    # Tool implementation
    result = perform_action(query)
    return result
```

Register tool:
```python
# In agents.py
from src.tools import new_tool_name

new_agent = create_agent(
    system_prompt,
    tools=[new_tool_name]  # Add to tools list
)
```

### 3. Modifying Prompts

Edit `src/prompts.py`:
```python
AGENT_SYSTEM_PROMPT = """
Enhanced prompt with new instructions...
"""
```

**Best Practices**:
- Be specific and detailed
- Include examples if needed
- Test prompt changes thoroughly
- Document why changes were made

### 4. Changing LLM Provider

Edit `src/agents.py`:
```python
# Option 1: Google Gemini
from langchain_google_genai import ChatGoogleGenerativeAI
llm = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash-exp",
    temperature=0,
    google_api_key=os.getenv("GOOGLE_API_KEY")
)

# Option 2: OpenAI
from langchain_openai import ChatOpenAI
llm = ChatOpenAI(
    model="gpt-4",
    temperature=0,
    openai_api_key=os.getenv("OPENAI_API_KEY")
)

# Option 3: Anthropic
from langchain_anthropic import ChatAnthropic
llm = ChatAnthropic(
    model="claude-3-opus-20240229",
    anthropic_api_key=os.getenv("ANTHROPIC_API_KEY")
)
```

### 5. Adding Custom Retrieval

Modify `src/rag.py`:
```python
def get_retriever(collection_name="custom_collection"):
    # Custom retriever logic
    vectorstore = get_or_create_collection(collection_name)
    return vectorstore.as_retriever(
        search_type="similarity",
        search_kwargs={"k": 5}
    )
```

### 6. Implementing Human-in-the-Loop

Add to state:
```python
class AgentState(TypedDict):
    # ... existing fields ...
    missing_info: Optional[List[str]]
    waiting_for_user: bool
```

Add node:
```python
def human_input_node(state: AgentState):
    if state.get("waiting_for_user"):
        # Pause and request input
        user_input = request_user_input(state["missing_info"])
        return {"user_provided_data": user_input, "waiting_for_user": False}
    return {}
```

## 🧪 Testing

### Running Tests
```bash
# All tests
pytest

# Specific test file
pytest tests/unit/test_tools.py

# With coverage
pytest --cov=src tests/

# Verbose output
pytest -v
```

### Writing Tests

**Unit Test Example**:
```python
# tests/unit/test_agents.py
from src.agents import orchestrator_agent
from langchain_core.messages import HumanMessage

def test_orchestrator_routing():
    result = orchestrator_agent.invoke({
        "messages": [HumanMessage(content="What is PM-KISAN?")]
    })
    assert result.next_agent == "POLICY_INTERPRETER"
```

**Integration Test Example**:
```python
# tests/integration/test_workflow.py
from src.graph import app

def test_full_workflow():
    inputs = {
        "input_text": "Am I eligible for PM-KISAN?",
        "messages": [HumanMessage(content="Am I eligible for PM-KISAN?")]
    }
    
    result = app.invoke(inputs, config={"configurable": {"thread_id": "test"}})
    
    assert "messages" in result
    assert len(result["messages"]) > 0
```

## 🐛 Debugging

### Enable Debug Logging
```python
# In logger.py
logging.basicConfig(
    level=logging.DEBUG,  # Change from INFO
    ...
)
```

### Use LangSmith Tracing
```bash
# In .env
LANGCHAIN_TRACING_V2=true
LANGCHAIN_API_KEY=your_api_key
LANGCHAIN_PROJECT=zynd-debug
```

View traces at [smith.langchain.com](https://smith.langchain.com)

### Python Debugger
```python
# Insert breakpoint
import pdb; pdb.set_trace()

# Or use VS Code debugger
# Set breakpoint in editor
```

### Inspect State
```python
# In any node
def my_node(state: AgentState):
    print("Current state:", state)
    # Node logic
```

## 📊 Performance Optimization

### 1. Enable Caching
Already implemented in `cache_helper.py`. To extend:
```python
from src.cache_helper import CacheHelper

cache_key = CacheHelper.hash_query(query, context)
cached = CacheHelper.get_llm_cache(cache_key)
if cached:
    return cached

result = expensive_operation()
CacheHelper.set_llm_cache(cache_key, result)
```

### 2. Batch Processing
```python
# Process multiple queries efficiently
results = llm.batch([
    [HumanMessage(content=q)] for q in queries
])
```

### 3. Async Operations
```python
# Use async for I/O operations
async def async_node(state):
    result = await some_async_operation()
    return {"result": result}
```

## 🎨 Code Style

### Follow PEP 8
```bash
# Install formatter
pip install black isort

# Format code
black src/
isort src/
```

### Type Hints
Always use type hints:
```python
from typing import List, Dict, Optional

def process_data(items: List[str]) -> Dict[str, int]:
    return {item: len(item) for item in items}
```

### Docstrings
```python
def complex_function(arg1: str, arg2: int) -> bool:
    """
    Brief description.
    
    Args:
        arg1: Description of arg1
        arg2: Description of arg2
        
    Returns:
        Description of return value
        
    Raises:
        ValueError: When arg2 is negative
    """
    pass
```

## 🔒 Security Best Practices

1. **Never commit API keys**
   - Use `.env` file
   - Add `.env` to `.gitignore`

2. **Validate inputs**
   - Use Pydantic for validation
   - Sanitize user inputs

3. **Rate limiting**
   - Implement rate limits for API calls
   - Handle quota errors gracefully

## 📦 Building for Production

### Environment-specific Config
```python
# config.py
import os

ENV = os.getenv("ENVIRONMENT", "development")

if ENV == "production":
    LOG_LEVEL = "WARNING"
    ENABLE_CACHE = True
else:
    LOG_LEVEL = "DEBUG"
    ENABLE_CACHE = False
```

### Docker Deployment
```dockerfile
# Dockerfile
FROM python:3.10-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY src/ ./src/
COPY .env .env

CMD ["python", "src/main.py"]
```

## 🤝 Contributing

### Git Workflow
```bash
# Create feature branch
git checkout -b feature/new-agent

# Make changes and commit
git add src/new_agent.py
git commit -m "Add: New agent for X functionality"

# Push and create PR
git push origin feature/new-agent
```

### Commit Message Format
```
Type: Brief description

- Detailed point 1
- Detailed point 2

Types: Add, Fix, Update, Remove, Refactor, Docs
```

## 📚 Learning Resources

- **LangGraph**: [docs.langchain.com/langgraph](https://docs.langchain.com/langgraph)
- **LangChain**: [python.langchain.com](https://python.langchain.com)
- **Pydantic**: [docs.pydantic.dev](https://docs.pydantic.dev)
- **ChromaDB**: [docs.trychroma.com](https://docs.trychroma.com)

## ❓ Troubleshooting Development Issues

### Issue: Import errors
**Solution**: Ensure Python path is correct
```python
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
```

### Issue: State not updating
**Solution**: Ensure node returns dict with fields to update
```python
# Correct
return {"field": value}

# Incorrect
state["field"] = value
return state
```

### Issue: Agent not routing correctly
**Solution**: Check orchestrator prompt and RouteDecision schema match

---

Next: [API Reference](api-reference.md) for complete schema documentation.
