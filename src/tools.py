from langchain_core.tools import tool
from src.config import get_zynd_agent
from src.rag import get_retriever
import json

@tool
def retrieve_policy(query: str) -> str:
    """
    PREMIUM TOOL: Retrieves detailed government policy information.
    Uses Zynd x402 protocol for authorized access to the policy database.
    """
    # Use POLICY agent identity
    zynd_agent = get_zynd_agent("POLICY")
    if zynd_agent:
        print(f"[Zynd Identity] Active: {zynd_agent.agent_config.identity_credential_path} (Seed ends in ...{zynd_agent.agent_config.secret_seed[-5:]})")
    
    # In a real scenario, this would be a paid API call via Zynd
    print(f"[Zynd Agent] Authorizing access for policy query: '{query}'")
    
    retriever = get_retriever()
    docs = retriever.invoke(query)
    
    if not docs:
        return "No specific policy found for this query."
        
    return "\n\n".join([f"Source: {d.metadata.get('source', 'Policy Doc')}\nContent: {d.page_content}" for d in docs])

@tool
def check_eligibility_rules(age: int, income: int, location: str, scheme_name: str) -> str:
    """
    Checks eligibility for a specific scheme based on user profile.
    Uses RAG to find the specific eligibility rules for the scheme.
    """
    # Use ELIGIBILITY agent identity
    zynd_agent = get_zynd_agent("ELIGIBILITY")
    if zynd_agent:
        print(f"[Zynd Identity] Active: {zynd_agent.agent_config.identity_credential_path}")

    query = f"eligibility rules for {scheme_name}"
    print(f"[Tool] Searching ChromaDB for: '{query}'")
    
    retriever = get_retriever()
    docs = retriever.invoke(query)
    
    if not docs:
        return f"Could not find specific eligibility rules for {scheme_name} in the database."
    
    # Return the rules found so the Agent can evaluate them against the profile
    rules_context = "\n".join([d.page_content for d in docs])
    return f"Found the following rules for {scheme_name}:\n{rules_context}\n\nPlease evaluate the user's profile (Age: {age}, Income: {income}, Location: {location}) against these rules."

@tool
def find_benefits_database(profile_summary: str) -> str:
    """
    Searches the benefits database for all schemes matching the profile summary.
    Uses RAG to find relevant schemes.
    """
    # Use BENEFIT agent identity
    zynd_agent = get_zynd_agent("BENEFIT")
    if zynd_agent:
        print(f"[Zynd Identity] Active: {zynd_agent.agent_config.identity_credential_path}")

    query = f"government schemes and benefits for {profile_summary}"
    print(f"[Tool] Searching ChromaDB for: '{query}'")
    
    retriever = get_retriever()
    docs = retriever.invoke(query)
    
    if not docs:
        return "No specific schemes found matching this profile."
        
    return "Found the following potential schemes:\n" + "\n\n".join([f"- {d.page_content} (Source: {d.metadata.get('source', 'Unknown')})" for d in docs])
