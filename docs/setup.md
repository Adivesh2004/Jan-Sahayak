# Setup Guide

This guide walks you through setting up the Zynd Protocols Application on your local machine.

## 📋 Prerequisites

- **Python**: 3.10 or higher
- **pip**: Latest version
- **Git**: For cloning the repository
- **API Keys**: 
  - Groq API key (for LLM)
  - Google API key (for embeddings)
  - LangSmith API key (optional, for tracing)

## 🚀 Installation

### Step 1: Clone the Repository

```bash
git clone <repository-url>
cd zynd-protocals-application
```

### Step 2: Create Virtual Environment

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**Linux/Mac:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

**Dependencies include:**
- `langchain` - LLM framework
- `langgraph` - Multi-agent orchestration
- `langchain-groq` - Groq LLM provider
- `langchain-google-genai` - Google embeddings
- `chromadb` - Vector database
- `pydantic` - Data validation
- `python-dotenv` - Environment management

### Step 4: Configure Environment Variables

Create a `.env` file in the project root:

```bash
# LLM Provider (Groq)
GROQ_API_KEY=your_groq_api_key_here

# Google (for embeddings)
GOOGLE_API_KEY=your_google_api_key_here

# LangSmith (Optional - for tracing/debugging)
LANGCHAIN_TRACING_V2=true
LANGCHAIN_ENDPOINT=https://api.smith.langchain.com
LANGCHAIN_API_KEY=your_langsmith_api_key_here
LANGCHAIN_PROJECT=zynd-protocols
```

**Get API Keys:**
- **Groq**: [https://console.groq.com](https://console.groq.com)
- **Google AI Studio**: [https://aistudio.google.com/app/apikey](https://aistudio.google.com/app/apikey)
- **LangSmith**: [https://smith.langchain.com](https://smith.langchain.com)

### Step 5: Verify Configuration

```bash
python check_env.py
```

This script checks if all required environment variables are set.

### Step 6: Prepare Vector Database

The application uses ChromaDB for RAG. Ensure you have policy documents loaded:

```bash
# If you have a chroma_db.zip file, extract it
unzip chroma_db.zip

# Otherwise, you'll need to populate the database with your documents
# (See Development Guide for details)
```

## 🎯 Running the Application

### Standard Mode

```bash
python src/main.py
```

You'll see the interactive CLI:

```
=============================================
Civic Assistance Agent System (Zynd Enhanced)
---------------------------------------------
Type 'exit' or 'quit' to stop.
=============================================

User (Question): 
```

### Streamlit UI Mode (Alternative)

```bash
streamlit run src/streamlit_app.py
```

Access the web interface at `http://localhost:8501`

## 🧪 Testing

Run the test suite:

```bash
# All tests
pytest

# Unit tests only
pytest tests/unit/

# Integration tests only
pytest tests/integration/

# With coverage
pytest --cov=src tests/
```

## ⚙️ Configuration

### LLM Provider Configuration

The default LLM is **Groq** (fast and cost-effective). To switch providers, edit [`src/agents.py`](file:///c:/Users/bhara/Desktop/Projects/zynd-protocals-application/src/agents.py):

**Use Google Gemini:**
```python
from langchain_google_genai import ChatGoogleGenerativeAI

llm = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash-exp",
    temperature=0,
    google_api_key=os.getenv("GOOGLE_API_KEY")
)
```

**Use Ollama (Local):**
```python
from langchain_ollama import ChatOllama

llm = ChatOllama(
    model="llama3.2:3b",
    temperature=0
)
```

### Logging Configuration

Logs are stored in `logs/` directory. Configure log level in [`src/logger.py`](file:///c:/Users/bhara/Desktop/Projects/zynd-protocals-application/src/logger.py):

```python
logging.basicConfig(
    level=logging.INFO,  # Change to DEBUG for verbose logging
    ...
)
```

### Cache Configuration

LLM response caching is enabled by default via [`src/cache_helper.py`](file:///c:/Users/bhara/Desktop/Projects/zynd-protocals-application/src/cache_helper.py). To disable:

```python
# In each agent file (policy_navigator.py, etc.)
# Comment out cache checks:
# cached_result = CacheHelper.get_llm_cache(cache_key)
```

## 🔍 Troubleshooting

### Issue: Import Errors

**Solution**: Ensure virtual environment is activated and dependencies are installed:
```bash
pip install -r requirements.txt
```

### Issue: API Rate Limits

**Solution**: 
- Check API key quotas
- Switch to a different LLM provider
- Enable caching to reduce API calls

### Issue: ChromaDB Not Found

**Solution**: Ensure `chroma_db/` directory exists:
```bash
# Check if directory exists
ls chroma_db/

# If missing, extract from backup
unzip chroma_db.zip
```

### Issue: Slow Performance

**Solutions**:
1. Use Groq instead of Ollama (20x faster)
2. Enable caching
3. Reduce retrieval chunk size in `rag.py`
4. Use smaller LLM model

### Issue: LangSmith Tracing Errors

**Solution**: LangSmith is optional. To disable, remove from `.env`:
```bash
# Comment out or remove these lines
# LANGCHAIN_TRACING_V2=true
# LANGCHAIN_API_KEY=...
```

## 📁 Project Structure

```
zynd-protocals-application/
├── src/
│   ├── main.py                      # Entry point
│   ├── graph.py                     # Main orchestrator
│   ├── agents.py                    # Agent configurations
│   ├── state.py                     # Main state definition
│   ├── schemas.py                   # Pydantic schemas
│   ├── policy_navigator.py          # Policy agent
│   ├── eligibility_verification.py  # Eligibility agent
│   ├── benefits_matching.py         # Benefits agent
│   ├── advocacy_agent.py            # Advocacy agent
│   ├── rag.py                       # RAG setup
│   ├── rag_agent.py                 # Agentic RAG
│   ├── tools.py                     # Shared tools
│   ├── prompts.py                   # System prompts
│   ├── config.py                    # Configuration
│   ├── logger.py                    # Logging setup
│   ├── cache_helper.py              # LLM caching
│   └── langsmith_config.py          # Tracing setup
├── tests/
│   ├── unit/                        # Unit tests
│   └── integration/                 # Integration tests
├── docs/                            # Documentation
├── chroma_db/                       # Vector database
├── logs/                            # Application logs
├── .env                             # Environment variables
├── requirements.txt                 # Python dependencies
└── README.md                        # Project README
```

## 🔄 Updating

To update dependencies:

```bash
pip install --upgrade -r requirements.txt
```

To update vector database with new documents:

```bash
# See Development Guide for document ingestion process
python scripts/ingest_documents.py
```

## 🐳 Docker Setup (Optional)

*Coming soon: Docker and docker-compose configurations*

## ✅ Verification Checklist

After setup, verify:

- [ ] Python 3.10+ installed
- [ ] Virtual environment activated
- [ ] All dependencies installed
- [ ] `.env` file configured with API keys
- [ ] `check_env.py` passes
- [ ] ChromaDB directory exists
- [ ] Application runs without errors
- [ ] Can interact via CLI
- [ ] Tests pass

---

Next: [Agents Reference](agents.md) to understand each agent's capabilities.
