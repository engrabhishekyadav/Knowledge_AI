# Complete End-to-End RAG System with PostgreSQL & pgvector

KnowledgeAI now features a complete, enterprise-grade **Retrieval-Augmented Generation (RAG)** pipeline powered by native **PostgreSQL + pgvector** and **Google Gemini** dense embeddings.

---

## 🏗️ Architecture Flow

```
User uploads document (.txt, .md, .doc)
         ↓
1. Document Ingestion & Text Extraction (document_parser.py)
         ↓
2. Semantic Markdown Text Chunking (rag_chunker.py)
   - Splits text into semantically coherent segments (600–700 chars)
   - 100-character sliding overlap window
   - Preserves section headings (H1, H2, H3)
         ↓
3. Dense Neural Vector Embeddings (embedding.py)
   - Generates 768-dimensional dense vectors using Google Gemini
   - Concurrent batch processing with asyncio semaphores
         ↓
4. PostgreSQL + pgvector Storage (chunk.py / rag_indexer.py)
   - Chunks stored in `document_chunks` table
   - Native `vector(768)` data type
   - Accelerated via Hierarchical Navigable Small World (HNSW) index
   - Cascading lifecycle: deleting a note cleans up all chunks
         ↓
User asks question in AI Copilot
         ↓
5. Query Vector Generation
   - Converts prompt into 768-dim query vector
         ↓
6. Native pgvector Cosine Distance Search (rag_retriever.py)
   - `SELECT ... ORDER BY embedding <=> query_vector LIMIT 4`
   - O(log N) fast nearest neighbor search via HNSW
         ↓
7. Context Formulation & LLM Grounding (agent.py)
   - Injects top-k retrieved chunks with explicit section citations
         ↓
8. Real-time Streaming (ai.py)
   - Gemini 3.5 Flash streams grounded answer via Server-Sent Events (SSE)
```

---

## 📦 Components Implemented

| File / Package | Description |
| :--- | :--- |
| `backend/app/models/chunk.py` | `DocumentChunk` model with native `pgvector.sqlalchemy.Vector(768)` column. |
| `backend/app/services/rag/chunker.py` | Semantic text chunker supporting Markdown headers, paragraphs, and overlap. |
| `backend/app/services/rag/indexer.py` | Orchestrates chunking, batch vector generation, and persistence into `document_chunks`. |
| `backend/app/services/rag/retriever.py` | Executes native pgvector `<=>` (cosine distance) similarity search with confidence scoring. |
| `backend/app/services/rag/reranker.py` | Reciprocal Rank Fusion (RRF) and lexical reranking with similarity cutoff. |
| `backend/app/services/embedding.py` | Gemini 768-dimensional dense vector embeddings with concurrent batching. |
| `backend/app/services/agent/` | Injects retrieved pgvector chunks into system prompt with section excerpts. |
| `backend/app/api/v1/notes.py` | Auto-indexes chunks on upload/create/update; adds `/notes/rag/search` and `/notes/{id}/chunks`. |
| `backend/app/api/v1/ai.py` | Integrates real-time vector retrieval into AI Copilot SSE streaming flow. |
| `backend/app/core/database.py` | Auto-creates `CREATE EXTENSION IF NOT EXISTS vector;` and HNSW cosine index. |

---

## 🧪 Automated Test Verification

Run the automated pytest test suite anytime from the `backend/` directory:
```bash
pytest tests/test_rag_services.py
```
Or run the interactive benchmark:
```bash
python scripts/test_rag_pipeline.py
```

All 6 validation steps have passed with **0 errors**:
1. PostgreSQL + pgvector Engine initialization & HNSW index verification.
2. Semantic Markdown text chunking with sliding overlap window.
3. Batch embedding generation & persistence in `document_chunks`.
4. High-accuracy vector retrieval using native `<=>` cosine distance.
5. AI Copilot streaming grounded in retrieved chunks.
6. Cascade deletion across foreign key links.
