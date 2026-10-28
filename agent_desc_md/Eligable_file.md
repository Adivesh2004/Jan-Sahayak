# Eligibility Agent – Citizen Advocacy & Eligibility Verification

## Vision

Create **agent advocates** that verify eligibility, interpret complex policies, and guide citizens with **trust‑backed recommendations**—ending bureaucratic opacity that costs people access to vital benefits.

The Eligibility Agent acts as a **digital caseworker** inside the Policy Navigator ecosystem, ensuring citizens clearly understand **what they qualify for, why, and what to do next**.

---

## The Challenge

Citizens frequently face:

* Complex and lengthy government policies
* Fragmented eligibility rules across departments
* Manual, error‑prone verification processes
* Lack of guidance during applications and appeals

As a result, **eligible citizens miss benefits they are legally entitled to**, causing frustration, inequality, and unmet social needs.

---

## Role of the Eligibility Agent

The Eligibility Agent **does not work in isolation**. It is explicitly designed to **consume, trust, and reason over the structured output of the Policy Interpretation Agent**.

Together, they form a two‑layer system:

```
Policy Interpretation Agent  →  Eligibility Agent  →  Citizen Guidance
        (What the policy means)     (What it means for YOU)
```

The Eligibility Agent translates **policy meaning into citizen‑specific decisions and actions**, ensuring communication is clear, consistent, and traceable back to official policy sources.

The Eligibility Agent bridges the gap between **policy rules and citizen reality**.

It answers:

* Am I eligible for this scheme?
* Why am I (or am I not) eligible?
* What benefits can I receive?
* What documents are required?
* Are there other schemes I also qualify for?
* What should I do if I’m rejected?

---

## Core Capabilities

### 1. Policy Interpretation

* Consumes structured outputs from the Policy Interpretation Agent
* Converts legal/policy rules into executable eligibility logic
* Explains rules in simple, citizen‑friendly language

---

### 2. Eligibility Verification

* Automatically evaluates citizen data against eligibility criteria
* Handles exceptions, edge cases, and conditional eligibility
* Provides transparent reasoning for every decision

Eligibility outcomes:

* Eligible
* Not eligible
* Conditionally eligible (missing or unclear information)

---

### 3. Benefit Matching

* Matches citizens across **multiple schemes and agencies**
* Identifies overlapping or complementary benefits
* Prioritizes high‑impact and time‑sensitive schemes

---

### 4. Citizen Advocacy

* Acts as a trusted guide through bureaucratic processes
* Provides step‑by‑step application instructions
* Generates document checklists
* Guides appeals and grievance filing when eligibility is denied

---

## Eligibility Agent Workflow (LangGraph)

```
Citizen Inputs
   ↓
Input Normalization & Validation
   ↓
Policy Interpretation Intake
   ↓
Eligibility Rule Evaluation
   ↓
Cross‑Scheme Benefit Matching
   ↓
Confidence & Risk Assessment
   ↓
Citizen Advocacy Guidance
   ↓
Structured + Human‑Readable Output
```

---

## Inputs

### Contract with Policy Interpretation Agent

The Eligibility Agent relies on a **strict, structured contract** from the Policy Interpretation Agent. This guarantees clarity, prevents hallucinations, and ensures explainability.

The following data is REQUIRED from the Policy Interpretation Agent:

* Policy metadata (name, authority, jurisdiction, version)
* Normalized eligibility rules (machine‑executable)
* Explicit exceptions and exclusions
* Benefits catalog
* Obligations and deadlines
* Identified ambiguities and risk flags
* Source citations (section‑level)

This structured policy output becomes the **single source of truth** for all eligibility decisions.

---

### Citizen‑Provided Information

### Citizen‑Provided Information

* Age
* Income
* Gender (if relevant)
* Category / Caste (if applicable)
* Disability status
* Employment status
* Education level
* Residency / location

### Policy‑Derived Information

* Eligibility rules
* Exceptions
* Benefits
* Deadlines
* Jurisdiction

---

## Logical Agent Nodes

> Each node explicitly references policy artifacts produced by the Policy Interpretation Agent, ensuring consistent language and reasoning.

### 1. Citizen Profile Validation Node

### 1. Citizen Profile Validation Node

Ensures inputs are usable and safe.

Responsibilities:

* Validate ranges and formats
* Detect missing or contradictory data
* Ask clarification questions
* Mask or redact sensitive fields

---

### 2. Eligibility Evaluation Node

Executes eligibility logic.

Capabilities:

* Boolean and threshold checks
* Exception handling
* Partial and conditional eligibility detection

---

### 3. Benefit Matching Node

Discovers **all applicable benefits**.

Responsibilities:

* Multi‑policy evaluation
* Cross‑agency matching
* Benefit deduplication
* Priority ranking

---

### 4. Confidence & Risk Assessment Node

Assesses reliability of conclusions.

Signals:

* Data completeness
* Policy ambiguity
* Rule clarity

Outputs:

* risk_level (low / medium / high)
* confidence_score

---

### 5. Citizen Advocacy Node

Provides guided assistance.

Delivers:

* Step‑by‑step application process
* Required documents checklist
* Deadlines and submission modes
* Appeal or grievance guidance
* Human escalation recommendation

---

## Structured Output Schema (JSON)

> All explanations and decisions include **policy traceability**, allowing citizens and auditors to understand *exactly* which policy clauses were applied.

````json

```json
{
  "citizen_profile_summary": {
    "age": 0,
    "income": 0,
    "category": "string",
    "location": "string"
  },
  "eligibility_result": {
    "status": "eligible | not_eligible | conditional",
    "reasoning": ["string"],
    "failed_conditions": ["string"],
    "exceptions_applied": ["string"]
  },
  "matched_benefits": [
    {
      "scheme_name": "string",
      "benefit_type": "monetary | service | reservation",
      "benefit_value": "string",
      "confidence_score": 0.0
    }
  ],
  "required_documents": ["string"],
  "next_steps": ["string"],
  "appeal_guidance": {
    "is_applicable": true,
    "reason": "string",
    "suggested_actions": ["string"]
  },
  "risk_level": "low | medium | high",
  "overall_confidence_score": 0.0,
  "citations": ["policy_section_reference"]
}
````

---

## Human‑Readable Output (Citizen View)

The Eligibility Agent should present:

* Clear eligibility verdict (Yes / No / Maybe)
* Simple explanation of why
* List of benefits the citizen qualifies for
* Required documents checklist
* Next actions with deadlines
* Confidence indicator and warnings

---

## Example (Simplified)

**Citizen Profile**

* Age: 21
* Income: ₹3,50,000
* Category: General

**Result**

* Eligible for: Student Scholarship Scheme
* Benefit: ₹50,000 per year
* Documents: Income certificate, Aadhaar, College ID
* Confidence: High

---

## Safety, Trust & Compliance

* No false guarantees
* Clear disclaimers for advisory nature
* PII protection and redaction
* High‑risk cases flagged for manual review
* Full audit trail of eligibility decisions

---

## Why This Agent Matters

✔ Ensures citizens don’t miss rightful benefits
✔ Builds trust through transparent reasoning
✔ Reduces bureaucratic friction
✔ Scales across departments and schemes
✔ Enables truly citizen‑centric digital governance

---

## Final Thought

> **Eligibility should not depend on how well someone understands bureaucracy.**

The Eligibility Agent ensures fairness by turning complex policy rules into **clear, actionable guidance for every citizen**.
