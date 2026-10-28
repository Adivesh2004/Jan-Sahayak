from typing import TypedDict, List, Optional, Any
from langgraph.graph import StateGraph, END
from langchain_core.messages import HumanMessage, SystemMessage
from src.eligibility_state import EligibilityState
from src.schemas import EligibilityAnalysisOutput, CitizenProfile
from src.agents import llm
from src.logger import setup_logger
from src.cache_helper import CacheHelper

logger = setup_logger("EligibilityAgent")

# --- Prompts ---

PROFILE_EXTRACTION_PROMPT = """
Extract citizen profile information from the user's query.
Look for: age, income, category/caste, location (state/district), education level, employment status, family size, special conditions (disability, widow, senior, etc.).

User query: {query}

If information is missing, leave it as null. Be conservative — only extract what is explicitly stated.
"""

# ENHANCED: Gold Standard Three-Tier Eligibility with "Why" Explanations
ELIGIBILITY_EVALUATION_PROMPT = """
You are an Eligibility Verification Expert using a three-tier status system.
Based on the citizen profile and general policy knowledge, evaluate eligibility.

Citizen Profile:
{profile}

User Question:
{query}

**THREE-TIER ELIGIBILITY STATUS (Choose one):**

✅ **ELIGIBLE** - Citizen clearly meets ALL known criteria
   - Use when: All essential criteria match
   - Include: "You qualify because [specific criteria match]"

⚠️ **POSSIBLY ELIGIBLE** - Likely qualifies but needs verification
   - Use when: Most criteria match but missing info or document verification needed
   - Include: "You likely qualify, but we need to verify [specific item]"

❌ **NOT ELIGIBLE** - Does not meet essential criteria
   - Use when: Fails one or more mandatory requirements
   - Include: "You don't qualify because [specific failed criteria]"
   - ALWAYS suggest alternatives if possible

**STATE-SPECIFIC VARIATIONS:**
Check for state-specific variations in eligibility rules for their location: {location}
Many schemes have different criteria per state — note any variations.

**ALWAYS INCLUDE "WHY" EXPLANATION:**
- For ELIGIBLE: "You qualify because your income (₹X) is below the ₹Y limit AND you are aged Z."
- For POSSIBLY ELIGIBLE: "You appear to qualify, but need to verify your income certificate."
- For NOT ELIGIBLE: "You don't qualify because the scheme requires age 60+ and you are 45. However, you may be eligible for [alternative]."

Provide a structured analysis with:
1. Three-tier eligibility status with explanation
2. Clear reasoning with specific criteria matches
3. Failed conditions if any (and why)
4. Alternative schemes if not eligible
5. Required documents with checklist
6. Confidence level (high/medium/low)
7. Next steps
"""

SYNTHESIS_PROMPT = """
You are a Citizen Advocate with a supportive, trust-building approach.
Based on the eligibility analysis below, provide a clear, empathetic Markdown response.

**LANGUAGE INSTRUCTION:**
The user has selected language: '{language}'.
- You MUST respond in '{language}'.
- Translate all headers, reasons, and instructions to '{language}'.
- Keep technical terms in English if translation would cause confusion, but explain them.

ANALYSIS:
{analysis}

**REQUIREMENTS:**

1. **Clear Status Header** (use appropriate one):
   - ✅ **Great News! You ARE Eligible**
   - ⚠️ **You're Likely Eligible (Needs Verification)**
   - ❌ **Unfortunately, You Don't Qualify for This Scheme**

2. **Why Explanation** (most important part):
   - Clearly explain why they got this status
   - Use their actual numbers: "Your income of ₹X is below the ₹Y limit"
   - Make it specific to THEIR situation

3. **What You Can Get** (if eligible):
   - Specific benefits and amounts
   - Timeline for receiving

4. **What's Needed** (document checklist):
   - [ ] Document 1
   - [ ] Document 2
   - Use checkbox format

5. **If Not Eligible** (special handling):
   - Be empathetic: "I know this isn't the news you hoped for"
   - Explain exactly what disqualified them
   - Suggest 2-3 alternative schemes they might qualify for
   - Offer hope: "Based on your profile, you may qualify for [X] instead"

6. **Next Steps**:
   - Clear, numbered action items
   - "Ready to apply? I can guide you step-by-step."

Output ONLY the Markdown response.
"""

# --- Nodes ---

def profile_extraction_node(state: EligibilityState):
    logger.info("Extracting citizen profile...")
    query = state["input_text"]
    try:
        structured_llm = llm.with_structured_output(CitizenProfile)
        prompt = PROFILE_EXTRACTION_PROMPT.format(query=query)
        
        profile = structured_llm.invoke([HumanMessage(content=prompt)])
        return {"citizen_profile": profile}
    except Exception as e:
        logger.error(f"Profile extraction failed: {e}")
        return {"citizen_profile": None}

def eligibility_evaluation_node(state: EligibilityState):
    logger.info("Evaluating eligibility...")
    query = state["input_text"]
    profile = state.get("citizen_profile")
    
    if not profile:
        profile_str = "No profile information provided"
        location = "Unknown"
    else:
        profile_str = str(profile.model_dump())
        location = profile.location or "Unknown"
    
    # Check cache
    cache_key = CacheHelper.hash_query(query, profile_str)
    cached_result = CacheHelper.get_llm_cache(cache_key)
    if cached_result:
        logger.info("Using cached eligibility result")
        return {"analysis_output": cached_result}
    
    try:
        structured_llm = llm.with_structured_output(EligibilityAnalysisOutput)
        prompt = ELIGIBILITY_EVALUATION_PROMPT.format(profile=profile_str, query=query, location=location)
        
        analysis = structured_llm.invoke([HumanMessage(content=prompt)])
        
        # Cache the result
        CacheHelper.set_llm_cache(cache_key, analysis)
        
        return {"analysis_output": analysis}
    except Exception as e:
        logger.error(f"Eligibility evaluation failed: {e}")
        return {"analysis_output": None}

def synthesis_node(state: EligibilityState):
    logger.info("Synthesizing citizen response...")
    analysis = state.get("analysis_output")
    language = state.get("language", "en")
    
    if not analysis:
        return {"final_markdown_response": "I'm sorry, I couldn't complete the eligibility check. Please provide more information."}
    
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
        return {"final_markdown_response": "Error generating response."}

# --- Graph Construction ---

def build_eligibility_graph():
    workflow = StateGraph(EligibilityState)
    
    workflow.add_node("profile_extraction", profile_extraction_node)
    workflow.add_node("eligibility_evaluation", eligibility_evaluation_node)
    workflow.add_node("synthesis", synthesis_node)
    
    workflow.set_entry_point("profile_extraction")
    workflow.add_edge("profile_extraction", "eligibility_evaluation")
    workflow.add_edge("eligibility_evaluation", "synthesis")
    workflow.add_edge("synthesis", END)
    
    return workflow.compile()

eligibility_graph = build_eligibility_graph()
