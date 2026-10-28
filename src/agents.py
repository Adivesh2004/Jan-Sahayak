from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field
from src.tools import retrieve_policy, check_eligibility_rules, find_benefits_database
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# --- LLM Configuration ---

# Using Google AI Studio (Gemini) - Fast option
# from langchain_google_genai import ChatGoogleGenerativeAI
# llm = ChatGoogleGenerativeAI(
#     model="gemini-2.0-flash-exp",
#     temperature=0,
#     google_api_key=os.getenv("GOOGLE_API_KEY")
# )

# Using Groq (ULTRA FAST - 20x faster than Ollama)
from langchain_groq import ChatGroq
llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    temperature=0,
    groq_api_key=os.getenv("GROQ_API_KEY")
)

# Ollama (TOO SLOW - causes 5+ minute delays)
# from langchain_ollama import ChatOllama
# llm = ChatOllama(model="qwen3:1.7b", temperature=0, stream=True)


from src.prompts import (
    ORCHESTRATOR_SYSTEM_PROMPT,
    POLICY_SYSTEM_PROMPT,
    ELIGIBILITY_SYSTEM_PROMPT,
    BENEFIT_SYSTEM_PROMPT,
    ADVOCACY_SYSTEM_PROMPT
)

# Reference alias for local usage if needed, or update usage below
orchestrator_system_prompt = ORCHESTRATOR_SYSTEM_PROMPT
policy_system_prompt = POLICY_SYSTEM_PROMPT
eligibility_system_prompt = ELIGIBILITY_SYSTEM_PROMPT
benefit_system_prompt = BENEFIT_SYSTEM_PROMPT
advocacy_system_prompt = ADVOCACY_SYSTEM_PROMPT

# --- Agents ---

def create_agent(system_prompt, tools=None):
    if tools:
        return ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("placeholder", "{messages}"),
        ]) | llm.bind_tools(tools)
    else:
        return ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("placeholder", "{messages}"),
        ]) | llm

# Initialize Agents
policy_agent = create_agent(policy_system_prompt, [retrieve_policy])
eligibility_agent = create_agent(eligibility_system_prompt, [check_eligibility_rules])
benefit_agent = create_agent(benefit_system_prompt, [find_benefits_database])
advocacy_agent = create_agent(advocacy_system_prompt)

# Orchestrator is slightly different, it yields a decision
from src.schemas import RouteDecision

# Orchestrator is slightly different, it yields a decision
# RouteDecision imported from schemas

orchestrator_agent = ChatPromptTemplate.from_messages([
    ("system", orchestrator_system_prompt),
    ("placeholder", "{messages}"),
]) | llm.with_structured_output(RouteDecision)
