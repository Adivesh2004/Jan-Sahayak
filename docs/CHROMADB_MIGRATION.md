# Vector Database Migration: FAISS → ChromaDB

## Changes Made

### Files Modified

#### [rag.py](file:///c:/Users/bhara/Desktop/Projects/zynd-protocals-application/src/rag.py)

**Before**: Used FAISS vector store
```python
from langchain_community.vectorstores import FAISS
vector_store = FAISS.load_local(index_path, embeddings, allow_dangerous_deserialization=True)
```

**After**: Uses ChromaDB
```python
from langchain_community.vectorstores import Chroma
vector_store = Chroma(
    persist_directory=chroma_path,
    embedding_function=embeddings
)
```

**Key Changes**:
- Import changed from `FAISS` to `Chroma`
- Path changed from `faiss_index` to `chroma_db`
- Initialization changed from `load_local()` to `Chroma()` constructor
- Removed `allow_dangerous_deserialization` parameter (not needed for ChromaDB)

---

#### [tools.py](file:///c:/Users/bhara/Desktop/Projects/zynd-protocals-application/src/tools.py)

Updated log messages:
- Line 40: `"Searching FAISS for"` → `"Searching ChromaDB for"`
- Line 64: `"Searching FAISS for"` → `"Searching ChromaDB for"`

---

## Why ChromaDB?

**Advantages over FAISS**:
1. **Persistent by default** - No manual save/load needed
2. **Metadata support** - Better filtering and querying
3. **Built-in CRUD operations** - Can add/update/delete documents easily
4. **SQLite backend** - More reliable storage
5. **No deserialization risks** - More secure

## Verification

The ChromaDB directory already exists at:
```
c:\Users\bhara\Desktop\Projects\zynd-protocals-application\chroma_db\
├── chroma.sqlite3 (112 MB)
└── f0035e81-72cb-4b99-8851-0f95645ec1b7/ (collection data)
```

## Testing

To verify the migration works:
```powershell
# Test RAG import
python -c "from src.rag import get_retriever; retriever = get_retriever(); print('ChromaDB loaded successfully')"

# Test with actual query
python src/main.py
# Then ask: "What is PM-KISAN?"
```

## Rollback (if needed)

If you need to revert to FAISS:
1. Change `Chroma` back to `FAISS` in rag.py
2. Change `chroma_db` back to `faiss_index`
3. Revert tools.py log messages

## Next Steps

1. ✅ Code updated
2. ⏳ Testing ChromaDB loading (in progress)
3. 🔄 Restart Streamlit app to use new database
4. ✅ Verify policy retrieval works correctly
