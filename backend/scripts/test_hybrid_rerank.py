import asyncio
import json
from sqlalchemy import select, func, text
from app.core.database import init_db_engine, async_session_factory
from app.models.note import Note
from app.models.chunk import DocumentChunk
from app.services.rag import (
    chunk_document_text,
    index_note_chunks,
    retrieve_relevant_chunks,
    filter_and_rerank_chunks,
)
from app.services.agent import stream_agent_response

SAMPLE_DOC_CONTENT = """# Modern Distributed Vector Databases and Hybrid Retrieval

## 1. System Architecture and Vector Representations
Traditional relational database management systems were designed for structured scalar queries.
With the proliferation of deep learning transformers, high-dimensional vector embeddings have become essential.
Each document chunk is mapped to a normalized 768-dimensional geometric coordinate space.
Dense semantic similarity is calculated using cosine distance in sub-milliseconds.

## 2. PostgreSQL Full-Text Search and Lexical Indexes
While vector search understands semantic conceptual intent, it can struggle with exact keyword matching.
Keywords such as serial IDs, medical drug names, or specific code syntax (`plainto_tsquery`, `vector_cosine_ops`) require inverted lexical indexes.
PostgreSQL provides robust Full-Text Search (FTS) using GIN indexes on `to_tsvector('english', content)` and ranking functions like `ts_rank_cd`.

## 3. Reciprocal Rank Fusion (RRF) Hybrid Search
Hybrid retrieval fuses dense vector nearest neighbors with sparse lexical BM25/FTS search results.
Reciprocal Rank Fusion computes a unified ranking score:
RRF(d) = (w_dense / (60 + rank_dense)) + (w_sparse / (60 + rank_sparse)).
This gives the user the best of both worlds: broad semantic intuition and exact keyword precision.

## 4. Similarity Thresholds and Anti-Hallucination Guardrails
Large language models have a tendency to hallucinate plausible-sounding answers when given low-confidence or irrelevant context.
By enforcing a strict similarity threshold cutoff (e.g., 0.35 minimum cosine similarity), the system discards noise.
If zero retrieved candidates pass the confidence threshold, the copilot explicitly alerts the user that the active document does not contain that information.

## 5. Cross-Encoder Precision Reranking
After candidates are collected via Hybrid RRF, a secondary precision reranker evaluates cross-attention and lexical density.
The reranker scores candidate chunks using query term coverage, section heading bonuses, and semantic alignment to produce the final top-k context window.
"""

async def run_hybrid_rerank_verification():
    print("==================================================================")
    print("  VERIFYING FEATURE 1 (HYBRID SEARCH) & FEATURE 2 (RERANKER + THRESHOLD)")
    print("==================================================================")

    # 1. Initialize Database Engine
    print("\n[STEP 1] Initializing PostgreSQL engine and verifying indexes...")
    await init_db_engine()
    
    test_note_id = "test-hybrid-feat-01"

    async with async_session_factory() as db:
        # Verify GIN and HNSW indexes exist
        gin_check = await db.execute(text(
            "SELECT indexname FROM pg_indexes WHERE tablename = 'document_chunks' AND indexname = 'ix_document_chunks_fts';"
        ))
        assert gin_check.scalar() is not None, "GIN index missing!"
        print("  - Verified GIN Full-Text Search index: OK")

        hnsw_check = await db.execute(text(
            "SELECT indexname FROM pg_indexes WHERE tablename = 'document_chunks' AND indexname = 'ix_document_chunks_embedding_hnsw';"
        ))
        assert hnsw_check.scalar() is not None, "HNSW vector index missing!"
        print("  - Verified HNSW pgvector index: OK")

        # Cleanup any previous test data
        existing = await db.execute(select(Note).where(Note.id == test_note_id))
        old_note = existing.scalar_one_or_none()
        if old_note:
            await db.delete(old_note)
            await db.commit()

        # 2. Persist Test Note and Index Chunks
        print("\n[STEP 2] Indexing test document with Gemini 768-d embeddings...")
        test_note = Note(
            id=test_note_id,
            title="Modern Distributed Vector Databases and Hybrid Retrieval",
            content=SAMPLE_DOC_CONTENT,
            category="Databases",
            tags=["pgvector", "RAG", "HybridSearch", "RRF"]
        )
        db.add(test_note)
        await db.commit()

        indexed_chunks = await index_note_chunks(db, test_note_id, SAMPLE_DOC_CONTENT)
        print(f"  - Indexed {len(indexed_chunks)} chunks successfully in PostgreSQL.")
        assert len(indexed_chunks) >= 5, "Expected at least 5 chunks"

        # 3. Test Feature 1: Hybrid Search (Dense + Sparse + RRF)
        print("\n[STEP 3] Testing Feature 1: Hybrid Search (Dense + Sparse FTS + RRF)...")
        
        # Exact keyword search where sparse FTS excels
        kw_query = "vector_cosine_ops plainto_tsquery"
        print(f"  Query A (Exact technical keywords): \"{kw_query}\"")
        kw_candidates = await retrieve_relevant_chunks(db, query=kw_query, note_id=test_note_id, top_k=6)
        assert len(kw_candidates) > 0, "Expected candidates from keyword query"
        top_kw = kw_candidates[0]
        print(f"    -> Top match: Section: '{top_kw['section']}' | Method: {top_kw['retrieval_method']} | RRF: {top_kw['rrf_score']}")
        assert "plainto_tsquery" in top_kw["content"] or "vector_cosine_ops" in top_kw["content"], "FTS should hit exact keyword chunk!"

        # Semantic conceptual search where dense pgvector excels
        semantic_query = "mathematical representations for understanding textual nuances"
        print(f"\n  Query B (Pure semantic search, no exact words): \"{semantic_query}\"")
        sem_candidates = await retrieve_relevant_chunks(db, query=semantic_query, note_id=test_note_id, top_k=6)
        assert len(sem_candidates) > 0, "Expected candidates from semantic query"
        top_sem = sem_candidates[0]
        print(f"    -> Top match: Section: '{top_sem['section']}' | Method: {top_sem['retrieval_method']} | Sim: {top_sem['similarity_score']}")
        assert top_sem["similarity_score"] > 0.40, "Dense similarity should be strong"

        # 4. Test Feature 2: Precision Reranking & Similarity Threshold Cutoff
        print("\n[STEP 4] Testing Feature 2: Precision Reranking & Similarity Threshold...")
        
        # 4a. In-domain query with reranking
        rag_query = "How does Reciprocal Rank Fusion combine dense and sparse rankings?"
        print(f"  Query: \"{rag_query}\"")
        candidates = await retrieve_relevant_chunks(db, query=rag_query, note_id=test_note_id, top_k=8)
        rerank_result = filter_and_rerank_chunks(
            query=rag_query,
            candidate_chunks=candidates,
            min_similarity=0.35,
            top_k=3
        )
        assert rerank_result["has_relevant_context"] is True, "Expected relevant context to be found"
        print(f"  - Candidates passed threshold: {rerank_result['passed_threshold_count']}/{rerank_result['total_candidates']}")
        print(f"  - Best rerank score: {rerank_result['best_score']}")
        for i, chk in enumerate(rerank_result["chunks"], 1):
            print(f"    [{i}] Section: '{chk['section']}' | Rerank: {chk['rerank_score']} | Lexical: {chk['lexical_score']} | Sim: {chk['similarity_score']}")

        # Ensure top reranked chunk is section 3 (RRF)
        assert "Reciprocal Rank Fusion" in rerank_result["chunks"][0]["section"]

        # 4b. Out-of-domain query (should FAIL similarity threshold)
        negative_query = "What is the secret recipe for strawberry chocolate ice cream?"
        print(f"\n  Negative/Irrelevant Query: \"{negative_query}\"")
        neg_candidates = await retrieve_relevant_chunks(db, query=negative_query, note_id=test_note_id, top_k=8)
        neg_rerank_result = filter_and_rerank_chunks(
            query=negative_query,
            candidate_chunks=neg_candidates,
            min_similarity=0.40,
            top_k=3
        )
        print(f"  - Has relevant context: {neg_rerank_result['has_relevant_context']}")
        print(f"  - Filtered chunks count: {len(neg_rerank_result['chunks'])}")
        assert neg_rerank_result["has_relevant_context"] is False, "Irrelevant query must NOT pass relevance threshold!"
        print("  -> Threshold Cutoff blocked irrelevant query from hallucinating! (SUCCESS)")

        # 5. Test Copilot Response with Threshold Guardrail
        print("\n[STEP 5] Testing Copilot Anti-Hallucination Guardrail in SSE stream...")
        token_count = 0
        streamed_response = ""
        async for chunk in stream_agent_response(
            prompt=negative_query,
            active_note=test_note.to_dict(),
            retrieved_chunks=neg_rerank_result["chunks"],
            has_relevant_context=neg_rerank_result["has_relevant_context"]
        ):
            if chunk.startswith("data: ") and chunk.strip() != "data: [DONE]":
                try:
                    payload = json.loads(chunk[6:].strip())
                    if payload.get("type") == "token":
                        streamed_response += payload.get("content", "")
                        token_count += 1
                except Exception:
                    pass

        print(f"  Streamed {token_count} tokens from Agent.")
        print("  Agent Guardrail Response Excerpt:")
        print("  " + "-" * 50)
        print("  " + streamed_response[:300].replace("\n", "\n  ") + "...")
        print("  " + "-" * 50)
        # Verify the model or fallback explains that the document does not contain this information
        lower_resp = streamed_response.lower()
        contains_guardrail = any(w in lower_resp for w in ["does not", "doesn't", "not contain", "not mention", "scope", "no information"])
        assert contains_guardrail, f"Response should indicate lack of context in document: {streamed_response[:200]}"
        print("  -> Anti-hallucination guardrail verified successfully!")

        # 6. Clean up test note
        print("\n[STEP 6] Cleaning up test note and cascading chunks...")
        await db.delete(test_note)
        await db.commit()
        remaining = (await db.execute(
            select(func.count(DocumentChunk.id)).where(DocumentChunk.note_id == test_note_id)
        )).scalar()
        assert remaining == 0
        print(f"  - Remaining chunks in DB: {remaining} (Cascade cleaned up)")

    print("\n==================================================================")
    print("  [SUCCESS] FEATURE 1 & FEATURE 2 VERIFICATION PASSED WITH 0 ERRORS!")
    print("==================================================================")

if __name__ == "__main__":
    asyncio.run(run_hybrid_rerank_verification())
