# Zynd Protocols Application - Documentation

Welcome to the **Zynd Protocols Application** documentation. This is a multi-agent civic assistance system designed to help citizens navigate government policies, check eligibility, discover benefits, and receive application guidance.

## 📚 Table of Contents

- [Architecture Overview](architecture.md) - System design and components
- [Setup Guide](setup.md) - Installation and configuration
- [Agents Reference](agents.md) - Detailed agent descriptions
- [State Management](state-management.md) - State types and transitions
- [Data Flow](data-flow.md) - Request/response flow patterns
- [Development Guide](development.md) - Contributing and extending
- [API Reference](api-reference.md) - Schemas, tools, and interfaces

## 🎯 What This System Does

The Zynd Protocols Application is an intelligent multi-agent system that provides:

1. **Policy Interpretation** - Translates complex policy documents into plain language
2. **Eligibility Verification** - Checks if citizens qualify for specific schemes
3. **Benefits Matching** - Discovers all benefits a citizen qualifies for
4. **Application Advocacy** - Guides citizens through application processes

## ⚡ Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your API keys

# Run the application
python src/main.py
```

## 🏗️ High-Level Architecture

```
User Query
    ↓
Orchestrator Agent (Routes to specialized agent)
    ↓
┌─────────────┬──────────────┬─────────────┬──────────────┐
│   Policy    │ Eligibility  │  Benefits   │   Advocacy   │
│  Navigator  │  Verifier    │   Matcher   │    Agent     │
└─────────────┴──────────────┴─────────────┴──────────────┘
    ↓
Formatted Response
```

## 🧩 Key Components

- **LangGraph** - Orchestrates multi-agent workflows
- **LangChain** - Provides LLM abstractions and tools
- **RAG System** - Retrieves relevant policy documents
- **Groq LLM** - Fast inference engine (ChatGroq)
- **Structured Outputs** - Type-safe responses via Pydantic

## 📊 Current Features

✅ Multi-agent orchestration with intelligent routing  
✅ Agentic RAG for document retrieval  
✅ Structured outputs with Pydantic schemas  
✅ LLM response caching for performance  
✅ Conversation memory with checkpointing  
✅ Comprehensive logging and tracing  
✅ Session history persistence  

## 🔜 Roadmap

- Human-in-the-loop for missing information
- Multi-agent pipeline collaboration
- Enhanced context sharing between agents
- Voice interface support
- Multi-language support

## 📖 Documentation Structure

Each documentation file serves a specific purpose:

- **architecture.md** - Deep dive into system design, patterns, and decisions
- **setup.md** - Step-by-step installation, configuration, and troubleshooting
- **agents.md** - Detailed description of each agent's capabilities and workflows
- **state-management.md** - State types, transitions, and data management
- **data-flow.md** - How requests flow through the system with examples
- **development.md** - Guide for developers to extend and contribute
- **api-reference.md** - Complete reference of schemas, tools, and APIs

## 🤝 Support

For issues, questions, or contributions, please refer to the [Development Guide](development.md).

---

**Version**: 1.0.0  
**Last Updated**: February 2026
