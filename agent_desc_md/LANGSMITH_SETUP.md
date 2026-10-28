# LangSmith Setup Guide

## Overview
LangSmith is integrated for tracing, debugging, and evaluating the multi-agent system.

## Setup Instructions

### 1. Get LangSmith API Key
1. Go to [smith.langchain.com](https://smith.langchain.com)
2. Sign up or log in
3. Navigate to Settings → API Keys
4. Create a new API key

### 2. Add to .env File
Add this line to your `.env` file:
```
LANGCHAIN_API_KEY=your_actual_api_key_here
```

Optional: Set a custom project name:
```
LANGCHAIN_PROJECT=civic-assistance-agent
```

### 3. Verify Integration
Run the application. You should see:
```
✅ LangSmith tracing enabled for project: civic-assistance-agent
```

If API key is missing:
```
⚠️ LangSmith API key not found. Tracing disabled.
```

## Features Enabled

### Automatic Tracing
- Every agent invocation is traced
- View full execution paths
- See individual LLM calls
- Monitor latency and tokens

### Evaluation Dataset
Run to create test dataset:
```bash
python src/evaluation.py
```

This creates a dataset with sample queries for:
- Policy interpretation
- Eligibility checks  
- Benefits matching
- Application guidance

### View Traces
Visit: https://smith.langchain.com/o/projects/p/civic-assistance-agent

## What Gets Traced

✅ Orchestrator routing decisions  
✅ RAG document retrieval  
✅ Policy Navigator pipeline  
✅ Eligibility evaluation  
✅ Benefits matching  
✅ Advocacy guidance  
✅ All LLM calls with prompts and outputs

## Tips

- **Filter by run type**: Focus on specific agents
- **Search by input**: Find traces for specific queries
- **Compare runs**: See performance changes over time
- **Export data**: Download traces for analysis
