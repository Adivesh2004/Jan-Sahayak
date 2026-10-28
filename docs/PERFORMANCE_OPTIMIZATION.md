# Performance Optimization Guide

## Current Performance Issues

### 🐌 Identified Bottlenecks

1. **Ollama qwen3:1.7b is TOO SLOW**
   - Average extraction: 5+ minutes
   - Benefits matching: 2-3 minutes  
   - Connection timeouts and errors
   
2. **Sequential LLM Calls**
   - 4-6 LLM calls per query (orchestrator + 3-5 agent nodes)
   - No parallelization

3. **Large Context Windows**
   - RAG retrieving 5 documents
   - Full document content passed to every node

---

## ⚡ Quick Fixes (Immediate)

### Option 1: Switch to Google Gemini (RECOMMENDED)

**Why**: 10-20x faster than local Ollama

**How**: Uncomment in `src/agents.py`:

```python
# Use Google Gemini instead of Ollama
from langchain_google_genai import ChatGoogleGenerativeAI

llm = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash-exp",  # Fastest model
    temperature=0,
    google_api_key=os.getenv("GOOGLE_API_KEY")
)
```

**Comment out Ollama**:
```python
# from langchain_ollama import ChatOllama
# llm = ChatOllama(model="qwen3:1.7b", temperature=0, stream=True)
```

**Expected Impact**: Queries complete in 30-60 seconds instead of 5-8 minutes

---

### Option 2: Use Groq (ULTRA FAST - FREE)

**Why**: Fastest inference (tokens/sec), free tier available

**How**: Add to `src/agents.py`:

```python
from langchain_groq import ChatGroq

llm = ChatGroq(
    model="llama-3.3-70b-versatile",  # or "mixtral-8x7b-32768"
    temperature=0,
    groq_api_key=os.getenv("GROQ_API_KEY")
)
```

**Expected Impact**: Queries in 15-30 seconds

---

## 🚀 Advanced Optimizations

### 1. Reduce RAG Documents

In `src/rag.py`:
```python
# Change from k=5 to k=2
return vector_store.as_retriever(search_kwargs={"k": 2})
```

**Impact**: 40% faster, still maintains quality

---

### 2. Simplify Agent Pipelines

Remove unnecessary nodes for simple queries:

**In `src/policy_navigator.py`**:
```python
# Skip intent detection for obvious policy questions
def should_skip_intent(query: str) -> bool:
    keywords = ["what is", "explain", "tell me about", "policy for"]
    return any(kw in query.lower() for kw in keywords)
```

**Impact**: 1 fewer LLM call = 20-30% faster

---

### 3. Parallel Node Execution

Where possible, run nodes in parallel (currently all sequential).

---

### 4. Aggressive Caching

Enable in `.env`:
```
LANGCHAIN_CACHE=true
```

**Impact**: Repeated queries instant

---

### 5. Reduce Token Limits

In prompts, add:
```python
"Be extremely concise. Maximum 200 words."
```

**Impact**: 30% faster generation

---

## 📊 Performance Targets

| Configuration | Current | After Gemini | After Groq |
|--------------|---------|--------------|------------|
| Simple Query | 5-8 min | 30-60 sec | 15-30 sec |
| Complex Query | 8-12 min | 1-2 min | 45-90 sec |
| Cached Query | 5-8 min | ~1 sec | ~1 sec |

---

## ✅ Recommended Immediate Action

**Switch to Groq** (you already have the API key):

1. Edit `src/agents.py` line 23-24
2. Replace Ollama with Groq
3. Restart application

**Single change, 20x speedup!**
