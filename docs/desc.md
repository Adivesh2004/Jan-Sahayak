# Civic Assistance Agent System

A production-grade, multi-agent AI system for **policy interpretation, eligibility verification, benefit matching, and citizen advocacy**, built using **LangGraph**, **RAG**, and **Google AI Studio (Gemini APIs)**.

---

## 1. System Overview

This system helps citizens:

* Understand complex government policies
* Verify eligibility for schemes
* Discover *all* benefits they qualify for
* Get guided support for applications, appeals, and grievances

The architecture is **agentic, modular, auditable, and scalable**, suitable for government, NGO, or civic-tech deployments.

---

## 2. Core Agents (Clear Responsibilities)

### 2.1 Orchestrator Agent (Coordinator)

**Role**: Central brain that routes tasks and manages state.

**Responsibilities**:

* Parse user intent (policy query, eligibility check, benefits, application, appeal)
* Maintain global workflow state
* Invoke the correct downstream agents
* Handle retries and fallbacks

**Error Handling**:

* If intent confidence < threshold → ask clarification
* If downstream agent fails → retry or route to human escalation

**Collaboration**:

* Calls *all* other agents
* Receives structured outputs and updates state

---

### 2.2 Policy Interpretation Agent

**Role**: Simplifies complex government documents.

**Inputs**:

* Policy PDFs, circulars, notifications
* Citizen question/context

**Outputs**:

* Plain-language explanation
* Key rules, deadlines, penalties
* What applies to the specific citizen

**RAG Usage**:

* Vector DB with indexed government policies
* Chunked by section, clause, date

**Error Handling**:

* If policy not found → ask for jurisdiction or scheme name
* If outdated policy → flag and warn

**Collaboration**:

* Sends interpreted rules to Eligibility Verification Agent

---

### 2.3 Eligibility Verification Agent

**Role**: Determines whether a citizen qualifies for a scheme.

**Inputs**:

* Citizen profile (age, income, caste, location, etc.)
* Rules from Policy Interpretation Agent

**Outputs**:

* Eligible / Not eligible
* Exact reason for rejection
* Fixable vs non-fixable conditions

**Logic**:

* Rule-engine + LLM explanation layer

**Error Handling**:

* Missing data → request specific fields
* Conflicting data → ask for confirmation

**Collaboration**:

* Passes eligible profile to Benefit Matching Agent
* Sends rejection explanations back to Orchestrator

---

### 2.4 Benefit Matching Agent

**Role**: Finds *all* benefits a citizen qualifies for across agencies.

**Inputs**:

* Verified citizen profile
* Eligibility constraints

**Outputs**:

* List of schemes (Central / State / Local)
* Benefit value, deadlines, urgency

**RAG Usage**:

* Persistent benefits knowledge base
* Tagged by eligibility criteria

**Error Handling**:

* No matches → explain why + suggest near-miss programs

**Collaboration**:

* Hands selected benefit to Citizen Advocacy Agent

---

### 2.5 Citizen Advocacy Agent

**Role**: Guided support through applications, status tracking, and appeals.

**Sub-Agents**:

* Document Guidance Agent
* Application Process Agent
* Status Tracking Agent
* Appeals & Grievance Agent

**Capabilities**:

* Step-by-step application walkthrough
* Explain portal errors in simple terms
* Draft appeals and grievances

**Error Handling**:

* Portal failure → provide retry steps
* Missed deadlines → suggest alternative remedies

**Collaboration**:

* Uses eligibility + benefit data
* Can escalate to Human Advocate

---

### 2.6 Compliance & Validation Agent (Silent Guard)

**Role**: Ensures legal, ethical, and procedural correctness.

**Responsibilities**:

* Jurisdiction validation
* Deadline enforcement
* Prevent illegal advice or document forgery

**Execution**:

* Runs in background on every agent output

---

## 3. Agent Executors

Each agent is executed as a **LangGraph node**.

**Executor Types**:

* LLM Executor (Gemini via Google AI Studio)
* Tool Executor (status check, portal scraping, APIs)
* Rule Executor (eligibility logic)

**Retry Strategy**:

* Soft retry (re-prompt)
* Hard retry (fallback agent)
* Human escalation

---

## 4. Data Flow (End-to-End)

1. User input → Orchestrator
2. Policy text retrieved via RAG
3. Eligibility rules derived
4. Citizen profile validated
5. Benefits matched
6. Application / appeal guidance delivered
7. Status tracked over time

All transitions are **state-driven**.

---

## 5. Data Storage Architecture

### 5.1 Persistent Databases

* **Vector DB** (existing):

  * Government policies
  * Scheme rules
  * FAQs

* **Relational / Document DB**:

  * Citizen workflow state
  * Application IDs
  * Appeal drafts

### 5.2 Data Retention

* Personally identifiable data minimized
* Session-based expiry
* Optional anonymization

---

## 6. RAG Architecture

* Embedding model: Google Gemini Embeddings
* Chunk size: 500–800 tokens
* Metadata:

  * Jurisdiction
  * Effective date
  * Scheme type

**Retrieval Strategy**:

* Hybrid (semantic + keyword)
* Recency bias

---

## 7. Google AI Studio Integration

### API Usage

* Model: Gemini Pro / Gemini Flash
* Tasks:

  * Policy summarization
  * Eligibility reasoning
  * Appeal drafting

### Configuration

* API keys stored in environment variables
* Rate limiting per agent
* Logging enabled for audits

---

## 8. Error Handling Strategy (System-Wide)

| Layer  | Handling              |
| ------ | --------------------- |
| Input  | Clarification prompts |
| Agent  | Retry + fallback      |
| Data   | Validation checks     |
| Legal  | Compliance agent      |
| System | Human escalation      |

---

## 9. Collaboration Model

* Agents communicate via **structured JSON state**
* No free-form chaining
* Deterministic transitions

---

## 10. Security & Privacy

* No document forgery assistance
* No legal impersonation
* Consent-based data usage
* Audit logs for decisions

---

## 11. Deployment Readiness

* Stateless agents
* Persistent workflow state
* Horizontal scaling
* Observability hooks

---

## 12. Future Enhancements

* Multilingual support
* Voice-based access
* WhatsApp integration
* NGO / Legal clinic dashboards

---

## 13. Summary

This system delivers **explainable, trustworthy, and actionable civic assistance** using modern agentic AI patterns while remaining compliant, auditable, and production-ready.
