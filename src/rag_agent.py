"""
Agentic RAG - A LangChain agent that intelligently retrieves policy documents.
"""
from typing import List
try:
    from langchain.agents import AgentExecutor, create_tool_calling_agent
except ImportError:
    # Fallback for different LangChain versions
    from langchain_core.runnables import RunnablePassthrough
    AgentExecutor = None
    create_tool_calling_agent = None

from langchain_core.tools import Tool
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage, AIMessage
from src.rag import get_retriever
from src.agents import llm
from src.logger import setup_logger
from src.cache_helper import CacheHelper

logger = setup_logger("RAGAgent")

# --- RAG Tool ---

def retrieve_policy_documents(query: str) -> str:
    """
    Retrieve relevant policy documents based on the query.
    Use this when you need to find specific policy information.
    """
    # Check cache first
    cache_key = CacheHelper.hash_query(query, "rag")
    cached_docs = CacheHelper.get_rag_cache(cache_key)
    
    if cached_docs:
        logger.info(f"Using cached RAG results for: {query[:50]}...")
        return cached_docs
    
    try:
        retriever = get_retriever()
        docs = retriever.invoke(query)
        
        # Format documents
        if not docs:
            result = "No relevant policy documents found."
        else:
            result = "\n\n---\n\n".join([
                f"**Document {i+1}**:\n{doc.page_content}" 
                for i, doc in enumerate(docs)
            ])
        
        # Cache the result
        CacheHelper.set_rag_cache(cache_key, result)
        
        logger.info(f"Retrieved {len(docs)} documents for: {query[:50]}...")
        return result
    except Exception as e:
        logger.error(f"RAG retrieval failed: {e}")
        return f"Error retrieving documents: {str(e)}"

# Create the retrieval tool
retrieval_tool = Tool(
    name="retrieve_policy_documents",
    description="Retrieves relevant policy documents from the knowledge base. Use this when you need specific policy information, regulations, or legal text.",
    func=retrieve_policy_documents
)

def rag_agent_retrieve(query: str) -> str:
    """
    Helper function for other agents to use RAG.
    Directly calls the retrieval tool for reliability.
    """
    try:
        # Direct retrieval - more reliable than complex agent
        result = retrieve_policy_documents(query)
        logger.info(f"RAG retrieval completed for: {query[:50]}...")
        return result
    except Exception as e:
        logger.error(f"RAG retrieval failed: {e}")
        return f"Error retrieving documents: {str(e)}"
