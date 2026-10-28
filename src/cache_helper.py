"""
Caching utilities for expensive operations.
"""
from functools import lru_cache
import hashlib
import json
from typing import Any, Dict

class CacheHelper:
    """Helper class for caching expensive operations."""
    
    _llm_cache: Dict[str, Any] = {}
    _rag_cache: Dict[str, Any] = {}
    
    @staticmethod
    def hash_query(query: str, context: str = "") -> str:
        """Generate hash for caching key."""
        combined = f"{query}|{context}"
        return hashlib.md5(combined.encode()).hexdigest()
    
    @staticmethod
    def get_llm_cache(key: str) -> Any:
        """Get cached LLM result."""
        return CacheHelper._llm_cache.get(key)
    
    @staticmethod
    def set_llm_cache(key: str, value: Any):
        """Cache LLM result."""
        # Limit cache size to prevent memory issues
        if len(CacheHelper._llm_cache) > 100:
            # Remove oldest entry (first key)
            first_key = next(iter(CacheHelper._llm_cache))
            del CacheHelper._llm_cache[first_key]
        CacheHelper._llm_cache[key] = value
    
    @staticmethod
    def get_rag_cache(key: str) -> Any:
        """Get cached RAG result."""
        return CacheHelper._rag_cache.get(key)
    
    @staticmethod
    def set_rag_cache(key: str, value: Any):
        """Cache RAG result."""
        if len(CacheHelper._rag_cache) > 50:
            first_key = next(iter(CacheHelper._rag_cache))
            del CacheHelper._rag_cache[first_key]
        CacheHelper._rag_cache[key] = value
    
    @staticmethod
    def clear_all():
        """Clear all caches."""
        CacheHelper._llm_cache.clear()
        CacheHelper._rag_cache.clear()
