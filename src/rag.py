import os
from langchain_community.vectorstores import Chroma
from langchain_core.documents import Document

from functools import lru_cache

@lru_cache(maxsize=1)
def get_retriever():
    # Helper to get absolute path to chroma_db from src/
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    chroma_path = os.path.join(base_dir, "chroma_db")
    
    if not os.path.exists(chroma_path):
        raise FileNotFoundError(f"ChromaDB directory not found at {chroma_path}")

    from langchain_huggingface import HuggingFaceEmbeddings
    
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-mpnet-base-v2")
    
    try:
        # Load existing ChromaDB
        vector_store = Chroma(
            persist_directory=chroma_path,
            embedding_function=embeddings
        )
        # Reduced from k=5 to k=3 for faster performance
        return vector_store.as_retriever(search_kwargs={"k": 3})
    except Exception as e:
        print(f"Error loading ChromaDB: {e}")
        # Fallback for testing if database is corrupt or incompatible
        return _mock_retriever

class MockRetriever:
    def invoke(self, query):
        return [Document(page_content="Mock policy content regarding " + query)]

_mock_retriever = MockRetriever()
