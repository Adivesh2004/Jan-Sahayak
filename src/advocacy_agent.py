from typing import TypedDict, List, Optional, Any
from langgraph.graph import StateGraph, END
from langchain_core.messages import HumanMessage, SystemMessage
from src.advocacy_state import AdvocacyState
from src.schemas import AdvocacyAnalysisOutput
from src.agents import llm
from src.logger import setup_logger
from src.cache_helper import CacheHelper

logger = setup_logger("AdvocacyAgent")

# --- Prompts ---

SCHEME_EXTRACTION_PROMPT = """
Identify the specific scheme or benefit the user wants to apply for from their query.
Also identify if this is:
- A NEW application
- A REJECTION/APPEAL situation
- A STATUS CHECK
- GENERAL guidance

User query: {query}

Return the scheme name and situation type. If no specific scheme, return "General Application Guidance".
"""

# ENHANCED: Gold Standard Application Guidance with Hand-Holding
ADVOCACY_ANALYSIS_PROMPT = """
You are a Citizen Advocate and Application Expert using a "hand-holding, not instruction" approach.
Help the citizen understand how to actually APPLY for and RECEIVE the benefit.

**YOUR APPROACH:**
- "Let's do this together. I'll guide you step-by-step."
- Never just give instructions — guide them through each step
- Anticipate obstacles and prepare them for each

Query: {query}
Scheme: {scheme}

**PROVIDE COMPREHENSIVE GUIDANCE INCLUDING:**

**1. Application Path** (online portal, office visit, or hybrid)
   - Specific website URLs if online
   - Office addresses and timing if offline
   - Which method is faster

**2. Document Checklist** with status tracking:
   - ✅ Essential documents (without these, application will fail)
   - 📋 Supporting documents (strengthen application)
   - ⚠️ Common missing documents that cause rejections

**3. Step-by-Step Submission**:
   - Break into numbered steps (Step 1 of 8, etc.)
   - Include "common mistakes at this step" warnings
   - Add validation checks ("Before moving to next step, verify...")

**4. After Submission**:
   - Expected timelines
   - How to check status
   - What each status means
   - When to follow up

**5. If Rejected** (CRITICAL - Most systems fail here):
   - Common rejection reasons and how to address each
   - Document correction guidance
   - Appeal process with deadlines
   - Alternative schemes to try

Focus on PRACTICAL, ACTIONABLE steps that prevent errors and rejections.
"""

# ENHANCED: Rejection and Appeal Handling
REJECTION_HANDLING_PROMPT = """
You are a Citizen Advocate helping someone whose application was rejected.
Your goal is to turn this setback into a success.

**USER SITUATION:**
{query}

**PROVIDE:**

1. **Plain Language Explanation**: Why they were likely rejected (no bureaucratic jargon)

2. **Can This Be Fixed?**: 
   - YES with corrections → Provide specific fix steps
   - NO but alternatives exist → Suggest other schemes
   - APPEAL possible → Explain appeal process

3. **Correction Steps** (if fixable):
   - What exactly needs to change
   - How to get correct documents
   - Where to resubmit

4. **Appeal Process** (if applicable):
   - Deadline for appeal
   - Step-by-step appeal process
   - What to write in appeal letter
   - Sample appeal language

5. **Escalation Options**:
   - 📞 Government helpline numbers
   - 🏢 NGO partners who can help
   - ⚖️ Legal aid services (if needed)
   - 👤 Request human caseworker assistance

6. **Alternative Schemes**: 
   - Other benefits they might qualify for
   - Suggest trying these in parallel

**TONE**: Empathetic but practical. "This is a setback, not the end. Here's exactly what we can do..."
"""

SYNTHESIS_PROMPT = """
You are a Digital Caseworker with a supportive, hand-holding approach.
Based on the advocacy analysis below, create a step-by-step guide that makes the citizen feel supported.

**LANGUAGE INSTRUCTION:**
The user has selected language: '{language}'.
- You MUST respond in '{language}'.
- Translate all headers, steps, and explanations to '{language}'.
- Keep technical terms in English if translation would cause confusion, but explain them.

ANALYSIS:
{analysis}

**REQUIREMENTS:**

1. **Warm Opening**: 
   - "I'm here to help you through this process."
   - If rejection: "I understand this is frustrating. Let's work through this together."

2. **Progress Tracker** (if applicable):
   📍 You are here → Step 2 of 6
   [Show visual progress]

3. **Document Checklist** with status:
   - [ ] Aadhaar Card
   - [ ] Income Certificate
   - [ ] Bank Statement
   (Use checkbox format)

4. **Step-by-Step with Warnings**:
   Each step should include:
   - Clear action
   - ⚠️ Common mistake to avoid
   - ✅ How to verify completion

5. **If Rejected** (special section):
   ### 🔄 What Went Wrong and How to Fix It
   - Plain language explanation
   - Specific correction steps
   - Appeal timeline
   - Escalation options

6. **Escalation Options** (always include):
   ### Need More Help?
   - 📞 Helpline: [relevant number]
   - 🏢 NGO Support: [if applicable]
   - ⚖️ Legal Aid: [for complex cases]
   - 👤 Request Human Caseworker

7. **Encouragement**: 
   "Don't give up! Many applications succeed on the second attempt."
   "Ready to start? I'll be here to guide you at each step."

Output ONLY the Markdown response.
"""

# --- Nodes ---

def scheme_extraction_node(state: AdvocacyState):
    logger.info("Identifying target scheme...")
    query = state["input_text"]
    try:
        prompt = SCHEME_EXTRACTION_PROMPT.format(query=query)
        response = llm.invoke([HumanMessage(content=prompt)])
        scheme = response.content.strip()
        return {"selected_scheme": scheme}
    except Exception as e:
        logger.error(f"Scheme extraction failed: {e}")
        return {"selected_scheme": "General Application Guidance"}

def advocacy_analysis_node(state: AdvocacyState):
    logger.info("Generating application guidance...")
    query = state["input_text"]
    scheme = state.get("selected_scheme", "General Scheme")
    
    # Check cache
    cache_key = CacheHelper.hash_query(query, scheme)
    cached_result = CacheHelper.get_llm_cache(cache_key)
    if cached_result:
        logger.info("Using cached advocacy result")
        return {"analysis_output": cached_result}
    
    try:
        structured_llm = llm.with_structured_output(AdvocacyAnalysisOutput)
        prompt = ADVOCACY_ANALYSIS_PROMPT.format(query=query, scheme=scheme)
        
        analysis = structured_llm.invoke([HumanMessage(content=prompt)])
        
        # Cache result
        CacheHelper.set_llm_cache(cache_key, analysis)
        
        return {"analysis_output": analysis}
    except Exception as e:
        logger.error(f"Advocacy analysis failed: {e}")
        return {"analysis_output": None}

def synthesis_node(state: AdvocacyState):
    logger.info("Synthesizing citizen guidance...")
    analysis = state.get("analysis_output")
    language = state.get("language", "en")
    
    if not analysis:
        return {"final_markdown_response": "I'm sorry, I couldn't generate application guidance at this moment. Please try again or contact a human caseworker."}
    
    try:
        analysis_dict = analysis.model_dump()
        prompt = SYNTHESIS_PROMPT.format(analysis=str(analysis_dict), language=language)
        
        response = llm.invoke([HumanMessage(content=prompt)])
        return {
            "final_markdown_response": response.content,
            "final_json_response": analysis_dict
        }
    except Exception as e:
        logger.error(f"Synthesis failed: {e}")
        return {"final_markdown_response": "Error generating guidance."}

# --- Graph Construction ---

def build_advocacy_graph():
    workflow = StateGraph(AdvocacyState)
    
    workflow.add_node("scheme_extraction", scheme_extraction_node)
    workflow.add_node("advocacy_analysis", advocacy_analysis_node)
    workflow.add_node("synthesis", synthesis_node)
    
    workflow.set_entry_point("scheme_extraction")
    workflow.add_edge("scheme_extraction", "advocacy_analysis")
    workflow.add_edge("advocacy_analysis", "synthesis")
    workflow.add_edge("synthesis", END)
    
    return workflow.compile()

advocacy_graph = build_advocacy_graph()
