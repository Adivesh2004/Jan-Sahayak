"""
LangSmith integration for tracing and evaluation.
"""
import os
from typing import Optional
from src.logger import setup_logger

logger = setup_logger("LangSmith")

def setup_langsmith():
    """
    Enable LangSmith tracing if API key is present.
    """
    langsmith_api_key = os.getenv("LANGCHAIN_API_KEY") or os.getenv("LANGSMITH_API_KEY")
    
    if langsmith_api_key:
        # Enable tracing
        os.environ["LANGCHAIN_TRACING_V2"] = "true"
        os.environ["LANGCHAIN_API_KEY"] = langsmith_api_key
        os.environ["LANGCHAIN_PROJECT"] = os.getenv("LANGCHAIN_PROJECT", "civic-assistance-agent")
        
        logger.info(f"✅ LangSmith tracing enabled for project: {os.environ['LANGCHAIN_PROJECT']}")
        return True
    else:
        logger.warning("⚠️ LangSmith API key not found. Tracing disabled. Add LANGCHAIN_API_KEY to .env to enable.")
        return False

def get_langsmith_url(run_id: Optional[str] = None) -> Optional[str]:
    """
    Generate LangSmith dashboard URL for a specific run.
    """
    if not os.getenv("LANGCHAIN_TRACING_V2"):
        return None
    
    project = os.getenv("LANGCHAIN_PROJECT", "civic-assistance-agent")
    base_url = "https://smith.langchain.com"
    
    if run_id:
        return f"{base_url}/o/runs/{run_id}"
    else:
        return f"{base_url}/o/projects/p/{project}"
