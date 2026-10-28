# Benefits Agent – Cross‑Scheme Benefit Discovery & Recommendation

## Vision

Create an **intelligent benefits discovery agent** that ensures no citizen misses out on benefits they are entitled to—by intelligently matching them across **multiple schemes, departments, and agencies**, and presenting results with **clear reasoning and trust‑backed recommendations**.

The Benefits Agent focuses on **maximizing citizen welfare**, not just validating eligibility for a single policy.

---

## The Problem It Solves

Even when citizens are eligible:

* Benefits are scattered across ministries and portals
* Citizens are unaware of overlapping or complementary schemes
* Information is outdated or inconsistent
* Manual discovery requires deep bureaucratic knowledge

Result: **Citizens receive less than they deserve.**

---

## Role of the Benefits Agent

The Benefits Agent works **downstream of the Policy Interpretation Agent and Eligibility Agent**.

```
Policy Interpretation Agent  →  Eligibility Agent  →  Benefits Agent  →  Citizen
   (Policy meaning)              (Can I qualify?)     (What all can I get?)
```

Its mission is to:

* Discover **all relevant benefits** a citizen qualifies for
* Rank and prioritize benefits based on impact and urgency
* Explain *why* each benefit applies
* Provide clear next steps to claim each benefit

---

## Core Capabilities

### 1. Cross‑Scheme Benefit Discovery

* Scans benefits across departments and agencies
* Works across central, state, and local schemes
* Avoids duplicate or conflicting benefits

---

### 2. Eligibility‑Aware Matching

* Uses **verified eligibility outputs**, not raw citizen data
* Honors policy exceptions and exclusions
* Supports partial and conditional eligibility

---

### 3. Benefit Prioritization & Ranking

Benefits are ranked using:

* Monetary or social impact
* Time sensitivity (deadlines)
* Citizen profile relevance
* Confidence level

---

### 4. Clear Benefit Explanation

Each benefit includes:

* What the benefit is
* Why the citizen qualifies
* What is required to claim it
* Where to apply

---

## Benefits Agent Workflow (LangGraph)

```
Eligibility Agent Output
   ↓
Benefit Catalog Intake
   ↓
Cross‑Policy Matching
   ↓
Conflict & Overlap Resolution
   ↓
Benefit Ranking & Scoring
   ↓
Explanation & Guidance
   ↓
Structured + Human Output
```

---

## Inputs

### From Eligibility Agent (Mandatory Contract)

The Benefits Agent **does not re‑evaluate eligibility**.
It relies on verified outputs from the Eligibility Agent.

Required inputs:

* Eligibility status per scheme
* Confidence scores
* Exceptions applied
* Citizen profile summary
* Policy citations

---

### From Policy Interpretation Agent

* Benefit definitions
* Validity periods
* Benefit constraints
* Scheme dependencies

---

## Logical Agent Nodes

### 1. Benefit Catalog Ingestion Node

Normalizes benefits across multiple policies.

Responsibilities:

* Standardize benefit types
* Normalize monetary values
* Attach policy metadata

---

### 2. Cross‑Scheme Matching Node

Matches citizen against **all eligible benefits**.

Responsibilities:

* Multi‑policy comparison
* Cross‑agency discovery
* Conditional benefit inclusion

---

### 3. Conflict & Overlap Resolution Node

Handles benefit interactions.

Examples:

* Mutually exclusive schemes
* Duplicate subsidies
* Dependency rules

---

### 4. Benefit Ranking & Scoring Node

Assigns priority scores.

Signals:

* Benefit value
* Urgency
* Confidence
* Citizen relevance

---

### 5. Benefit Guidance Node

Provides actionable guidance.

Delivers:

* How to claim
* Required documents
* Deadlines
* Application channels

---

## Structured Output Schema (JSON)

```json
{
  "citizen_profile_summary": {
    "location": "string",
    "category": "string"
  },
  "eligible_benefits": [
    {
      "scheme_name": "string",
      "benefit_type": "monetary | service | reservation",
      "benefit_value": "string",
      "priority_rank": 1,
      "confidence_score": 0.0,
      "why_you_qualify": ["string"],
      "policy_references": ["section_reference"],
      "how_to_claim": {
        "steps": ["string"],
        "required_documents": ["string"],
        "deadline": "string",
        "application_mode": "online | offline | hybrid"
      }
    }
  ],
  "conflicts_or_exclusions": [
    {
      "benefit_a": "string",
      "benefit_b": "string",
      "reason": "string"
    }
  ],
  "overall_confidence_score": 0.0
}
```

---

## Human‑Readable Output (Citizen View)

The Benefits Agent should present:

* A prioritized list of benefits
* Clear explanation for each benefit
* Visual urgency indicators
* Step‑by‑step claiming guidance
* Confidence and trust indicators

---

## Example (Simplified)

**Citizen:** 21‑year‑old student, income ₹3,50,000

**Top Benefits:**

1. Student Scholarship Scheme – ₹50,000/year
2. Education Fee Reimbursement – Tuition covered

**Why:** Income and age criteria satisfied across both schemes

---

## Safety, Trust & Governance

* No guaranteed outcomes
* Strict dependency on upstream agents
* Policy‑grounded explanations
* Audit trail for benefit recommendations
* High‑risk or low‑confidence benefits flagged

---

## Why This Agent Matters

✔ Maximizes citizen benefit discovery
✔ Reduces information asymmetry
✔ Prevents benefit loss due to ignorance
✔ Encourages equitable access
✔ Enables citizen‑centric governance

---

## Final Thought

> **Benefits should be discovered automatically—not by luck or insider knowledge.**

The Benefits Agent ensures every eligible citizen sees the **full picture of support available to them**, clearly and transparently.
