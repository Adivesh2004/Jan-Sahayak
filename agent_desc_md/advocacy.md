# Citizen Guidance & Application Agent – Advocacy‑Driven Caseworker

## Vision

Create a **citizen advocacy agent** that does more than provide information—it **actively guides, supports, and stands with citizens** through application, submission, follow‑up, and appeal processes.

This agent exists to ensure that **eligibility and benefits actually convert into outcomes**, eliminating the last mile of bureaucratic failure.

---

## The Problem This Agent Solves

Even when citizens:

* Understand policies
* Are confirmed eligible
* Know the benefits they qualify for

They still fail to receive benefits because:

* Application processes are complex
* Documentation requirements are unclear
* Deadlines are missed
* Rejections are poorly explained
* Appeals are intimidating

This agent addresses the **execution gap** in public welfare systems.

---

## Role in the Agent Ecosystem

The Citizen Guidance & Application Agent works **downstream of all reasoning agents**.

```
Policy Interpretation Agent  →  Eligibility Agent  →  Benefits Agent
                                                ↓
                                   Citizen Guidance / Application Agent
                                                ↓
                                           Real‑World Outcome
```

It transforms **decisions into actions**.

---

## Core Responsibilities

### 1. Application Guidance

* Explain application steps in simple language
* Adapt guidance based on citizen profile and benefit type
* Provide channel‑specific instructions (online / offline / hybrid)

---

### 2. Document Advocacy

* Generate personalized document checklists
* Explain how to obtain missing documents
* Flag risky or commonly rejected documents

---

### 3. Submission Support

* Guide citizens during form filling
* Validate inputs before submission
* Reduce errors that cause rejection

---

### 4. Follow‑Up & Status Guidance

* Explain application status meanings
* Guide follow‑up actions
* Advise on timelines and escalation paths

---

### 5. Rejection & Appeal Advocacy

* Interpret rejection reasons
* Determine appeal eligibility
* Provide step‑by‑step appeal guidance
* Recommend human assistance when required

---

## Advocacy‑First Design Principles

* Citizen‑first language (no bureaucratic jargon)
* Transparency over optimism
* No false guarantees
* Clear accountability trails
* Escalate to humans when trust is at risk

---

## Citizen Guidance Workflow (LangGraph)

```
Selected Benefit
   ↓
Application Requirement Intake
   ↓
Document Readiness Check
   ↓
Application Path Selection
   ↓
Submission Guidance
   ↓
Status Monitoring
   ↓
Appeal / Escalation (if needed)
   ↓
Outcome Summary
```

---

## Inputs

### From Benefits Agent (Mandatory)

* Selected scheme / benefit
* Benefit type and value
* Eligibility confirmation
* Confidence score
* Required documents
* Policy citations

---

### From Citizen

* Available documents
* Preferred application mode
* Language preference
* Accessibility needs

---

## Logical Agent Nodes

### 1. Application Requirement Node

Determines application flow.

Outputs:

* Application portal or office
* Online/offline steps
* Submission deadlines

---

### 2. Document Readiness Node

Assesses document completeness.

Capabilities:

* Missing document detection
* Risk flagging
* Alternative document suggestions

---

### 3. Submission Guidance Node

Acts like a live caseworker.

Provides:

* Field‑by‑field guidance
* Common mistake warnings
* Pre‑submission checklist

---

### 4. Status & Follow‑Up Node

Explains post‑submission stages.

Examples:

* Under review
* Rejected
* Approved

Includes escalation guidance.

---

### 5. Appeal & Escalation Node

Activated on rejection or delay.

Provides:

* Appeal eligibility
* Draft appeal checklist
* Timelines and offices
* Legal aid / human support recommendation

---

## Structured Output Schema (JSON)

```json
{
  "selected_scheme": "string",
  "application_path": {
    "mode": "online | offline | hybrid",
    "portal_or_office": "string",
    "deadline": "string"
  },
  "document_status": {
    "ready": ["string"],
    "missing": ["string"],
    "high_risk": ["string"]
  },
  "submission_guidance": {
    "steps": ["string"],
    "common_mistakes": ["string"],
    "validation_checks": ["string"]
  },
  "post_submission": {
    "expected_timelines": "string",
    "status_meanings": {
      "under_review": "string",
      "rejected": "string",
      "approved": "string"
    }
  },
  "appeal_support": {
    "eligible": true,
    "reason": "string",
    "steps": ["string"],
    "escalation_options": ["string"]
  },
  "overall_confidence": 0.0,
  "citations": ["policy_or_process_reference"]
}
```

---

## Human‑Readable Output (Citizen View)

The app should show:

* Clear “What to do now” guidance
* Document checklist with progress indicators
* Deadlines and reminders
* Simple explanations of status updates
* Appeal help when things go wrong

---

## Example (Simplified)

**Benefit:** Student Scholarship Scheme

* Apply via: State Scholarship Portal
* Deadline: 31 Oct
* Missing document: Income Certificate
* Next step: Apply at MeeSeva / Revenue Office

If rejected:

* Appeal allowed within 15 days
* Submit revised income proof

---

## Safety, Trust & Ethics

* No submission on behalf of citizen without consent
* Clear disclaimers
* Data minimization and PII protection
* Escalation for vulnerable cases
* Full audit trail of guidance provided

---

## Why This Agent Is Critical

✔ Converts eligibility into real benefits
✔ Reduces drop‑offs and rejections
✔ Builds citizen trust
✔ Acts as a digital advocate
✔ Completes the welfare delivery loop

---

## Final Thought

> **Eligibility without advocacy is incomplete.**

The Citizen Guidance & Application Agent ensures that every eligible citizen is **supported until the outcome—not abandoned after advice**.
