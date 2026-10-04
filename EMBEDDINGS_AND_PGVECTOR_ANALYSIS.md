# Deep Dive: Embeddings, pgvector, and RAG Implementation in KnowledgeAI

This document explains how **Embeddings**, **pgvector**, and **RAG (Retrieval-Augmented Generation)** are actually implemented in this project, why embeddings are stored in JSON, and what the architectural differences are between the current implementation and a native PostgreSQL `pgvector` pipeline.

---

## 📌 Executive Summary

Your observation is **100% accurate**:

1. **`pgvector` is installed as a dependency, but is NOT actively used in the database queries.**
2. **Embeddings are stored as a JSON array (`List[float]`)**, not a native PostgreSQL `vector` type.
3. **Embeddings are generated via custom Python code (NumPy feature hashing)**, rather than an external embedding model API or local Transformer model.
4. **Vector Search is performed in Python application memory**, rather than inside the PostgreSQL database engine using index operators (`<->` / `<=>`).
5. **RAG in the AI Copilot works via Direct Context Injection** (prompt-grounding with the active note), rather than chunked vector retrieval.

---

## 🔍 Detailed Code Audit

### 1. The Database Model: Stored in JSON
In [`backend/app/models/note.py`](file:///C:/Users/HP/Desktop/Knowledge_AI_Workspace/backend/app/models/note.py#L18-L19):
```python
# Vector embedding representation (supports JSON array or pgvector column)
embedding: Mapped[Optional[List[float]]] = mapped_column(JSON, nullable=True)
```
- **What this does:** When a note is created or updated, its 384-dimensional float vector is serialized as a JSON string and saved into a generic `JSON` column in the database.
- **Why it was written this way:** This allows the application to work seamlessly on **both SQLite** (`knowledge_ai.db`) **and PostgreSQL**. If it used `from pgvector.sqlalchemy import Vector` and `mapped_column(Vector(384))`, **SQLite would immediately fail on startup** with a syntax error because SQLite has no native `VECTOR` type.

---

### 2. How Embeddings Are Generated (In-Memory Python Code)
In [`backend/app/services/embedding.py`](file:///C:/Users/HP/Desktop/Knowledge_AI_Workspace/backend/app/services/embedding.py#L5-L32):
```python
def generate_embedding(text: str, dimension: int = 384) -> List[float]:
    words = text.lower().replace("\n", " ").split()
    vector = np.zeros(dimension, dtype=np.float32)

    for i, word in enumerate(words):
        h = hash(word)
        pos = abs(h) % dimension
        weight = 1.0 / math.sqrt(i + 1)
        vector[pos] += weight

        pos2 = (abs(h >> 4) + 17) % dimension
        vector[pos2] += weight * 0.5

    norm = np.linalg.norm(vector)
    if norm > 0:
        vector = vector / norm
    return vector.tolist()
```
- **How it works:** It uses **Feature Hashing (the Hashing Trick)** and L2 normalization with NumPy.
- **Characteristics:**
  - ⚡ **Zero latency:** Runs in `< 1ms` locally on CPU.
  - 🆓 **Zero cost:** Requires no OpenAI embedding API credits or heavy 500MB PyTorch / HuggingFace model downloads.
  - ⚠️ **Limitation:** Feature hashing maps word tokens to vector dimensions via mathematical hash functions. It captures keyword co-occurrence and prefixes, but **does not have deep semantic understanding** (synonyms like "king" - "queen" or multilingual semantics) that true neural models like `text-embedding-3-small` or `all-MiniLM-L6-v2` provide.

---

### 3. How Semantic / Hybrid Search Actually Works
In [`backend/app/services/hybrid_search.py`](file:///C:/Users/HP/Desktop/Knowledge_AI_Workspace/backend/app/services/hybrid_search.py#L27-L56):
```python
stmt = select(Note)
res = await db.execute(stmt)
all_notes = res.scalars().all()

for note in all_notes:
    # 1. Semantic Cosine Similarity calculated in Python using NumPy
    note_embedding = note.embedding or generate_embedding(...)
    semantic_score = cosine_similarity(query_vector, note_embedding)

    # 2. Lexical Keyword match calculated in Python
    ...
    
    # 3. Hybrid combined score
    hybrid_score = (hybrid_weight * semantic_score) + ((1.0 - hybrid_weight) * lexical_score)
```
- Instead of running a SQL vector query like:
  ```sql
  SELECT * FROM notes ORDER BY embedding <=> '[0.12, 0.45, ...]' LIMIT 10;
  ```
- The backend loads the notes into Python memory and loops through them, computing cosine similarity using `np.dot()`.

---

### 4. How RAG (Retrieval-Augmented Generation) Works in the Copilot
In [`backend/app/services/agent.py`](file:///C:/Users/HP/Desktop/Knowledge_AI_Workspace/backend/app/services/agent.py) & [`backend/app/api/v1/ai.py`](file:///C:/Users/HP/Desktop/Knowledge_AI_Workspace/backend/app/api/v1/ai.py#L90-L97):
```python
# In ai.py:
if note_id:
    stmt = select(Note).where(Note.id == note_id)
    res = await db.execute(stmt)
    note = res.scalar_one_or_none()
    if note:
        active_note = note.to_dict()

# In agent.py:
async def stream_agent_response(prompt: str, active_note: Optional[Dict[str, Any]] = None, ...):
    # Active note text is inserted directly into the system prompt:
    active_doc_context = f"ACTIVE DOCUMENT TITLE: {active_note['title']}\nCONTENT:\n{active_note['content']}"
```
- **RAG Architecture Pattern:** This is **Full Document Grounding (Context Injection RAG)**.
- When you are viewing or have selected a document, the entire document is passed into Gemini's large context window (~1 million tokens for Gemini 3.5 Flash).
- This ensures 100% of the document's content is visible to the model without losing context across arbitrary chunk boundaries.

---

## ⚖️ Comparison Table: Current vs. True Native pgvector

| Feature | Current Implementation | Native PostgreSQL `pgvector` |
| :--- | :--- | :--- |
| **Database Engine** | Dual: Works on **SQLite** & PostgreSQL | **PostgreSQL only** (requires `pgvector` C-extension) |
| **Column Data Type** | `JSON` (`List[float]`) | `vector(384)` / `vector(1536)` |
| **Index Type** | None (in-memory scan) | HNSW or IVFFlat (`CREATE INDEX ... USING hnsw`) |
| **Search Execution** | Python RAM (`np.dot` in loop) | PostgreSQL C-engine (`ORDER BY embedding <=> query_vec`) |
| **Embedding Source** | Deterministic Python Hash | OpenAI `text-embedding-3-small` or HuggingFace `sentence-transformers` |
| **RAG Mechanism** | Active Note Prompt Injection | Chunking -> Vector DB Query -> Top K chunks injected |
| **Setup Complexity** | **Zero setup** (starts instantly on any machine) | Requires Docker / PostgreSQL installation + pgvector compile |
| **Scalability** | Ideal for up to ~10,000 personal notes | Scales to millions of document chunks |

---

## 💡 Why Was It Built This Way?

The developer chose this architecture deliberately to achieve **portability and zero-barrier local onboarding**:
1. If the project strictly required `pgvector`, anyone cloning the repo would have to install PostgreSQL, build `pgvector` binaries, and configure database users before running a single test.
2. By using a `JSON` column and NumPy cosine similarity, the codebase runs out-of-the-box on Windows, Mac, Linux, and SQLite with zero configuration.

---

## 🚀 How to Upgrade to Native pgvector (If Desired)

If you ever want to upgrade to a production-grade native `pgvector` pipeline:
1. **Require PostgreSQL**: Disable SQLite fallback.
2. **Use `Vector` column**:
   ```python
   from pgvector.sqlalchemy import Vector
   embedding = mapped_column(Vector(384), nullable=True)
   ```
3. **Use True Neural Embeddings**:
   Use `fastembed` or `sentence-transformers`:
   ```python
   from fastembed import TextEmbedding
   model = TextEmbedding(model_name="BAAI/bge-small-en-v1.5")
   embedding = list(model.embed([text]))[0].tolist()
   ```
4. **Query with pgvector operators**:
   ```python
   stmt = select(Note).order_by(Note.embedding.cosine_distance(query_vector)).limit(10)
   ```
