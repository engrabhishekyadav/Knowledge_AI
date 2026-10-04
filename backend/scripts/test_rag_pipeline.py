import asyncio
import httpx
from app.core.database import init_db_engine, get_db, async_session_factory
from app.models.note import Note
from app.models.chunk import DocumentChunk
from app.services.rag import chunk_document_text, index_note_chunks, retrieve_relevant_chunks
from app.services.agent import stream_agent_response
from sqlalchemy import select, func, text

SAMPLE_DOC_CONTENT = """# High-Performance RAG Architecture with PostgreSQL and pgvector

## 1. System Overview & Core Motivations
Retrieval-Augmented Generation (RAG) bridges the gap between static LLM training data and dynamic private enterprise knowledge.
Traditional lexical keyword search (BM25) struggles with semantic understanding, synonyms, and multi-lingual queries.
By converting text into dense mathematical vector spaces, semantic similarity can be computed in sub-milliseconds.

## 2. Chunking Strategies & Overlap Configuration
Raw documents must be split into semantically coherent segments before vectorization.
We employ a Recursive Character & Markdown Heading Splitter.
The target chunk size is configured to 700 characters with a 100 character sliding overlap window.
This preserves grammatical coherence and prevents critical context from being truncated at arbitrary line breaks.

## 3. Vector Embeddings with Google Gemini
Dense vector embeddings are computed using Google Gemini's dense embedding model.
Each text segment is transformed into a 768-dimensional normalized unit vector.
The 768-dimension space provides state-of-the-art MTEB retrieval accuracy while remaining computationally lightweight.

## 4. PostgreSQL Vector Indexing with HNSW
To scale vector retrieval to millions of chunks without linear brute-force table scans, we deploy Hierarchical Navigable Small World (HNSW) indexes.
In PostgreSQL, this is defined via `USING hnsw (embedding vector_cosine_ops)`.
HNSW constructs a multi-layer geometric graph structure, enabling approximate nearest neighbor (ANN) lookups in logarithmic time O(log N).

## 5. Security, Tenancy & Cascade Lifecycle
Every document chunk maintains a strict foreign key link to its parent note record: `FOREIGN KEY (note_id) REFERENCES notes(id) ON DELETE CASCADE`.
When a user modifies or deletes a note, PostgreSQL automatically cascades the deletion across all associated vector chunks.
"""

async def run_rag_test():
    print("==================================================================")
    print("  TESTING END-TO-END RAG PIPELINE (PostgreSQL + pgvector)")
    print("==================================================================")

    # 1. Initialize Database & Tables
    print("\n[STEP 1] Initializing PostgreSQL + pgvector Engine...")
    session_factory = await init_db_engine()
    print("Database Engine Initialized successfully!")

    async with async_session_factory() as db:
        # Check HNSW index
        idx_check = await db.execute(text(
            "SELECT indexname FROM pg_indexes WHERE tablename = 'document_chunks' AND indexname = 'ix_document_chunks_embedding_hnsw';"
        ))
        row = idx_check.fetchone()
        print(f"Verified HNSW index in PostgreSQL: {row is not None} ({row[0] if row else 'None'})")

        # 2. Test Text Chunking
        print("\n[STEP 2] Testing Semantic Text Chunking...")
        chunks_meta = chunk_document_text(SAMPLE_DOC_CONTENT, chunk_size=600, chunk_overlap=80)
        print(f"Generated {len(chunks_meta)} semantic chunks from sample document.")
        for c in chunks_meta:
            print(f"  - Chunk {c['chunk_index']} | Section: '{c['section']}' | Size: {c['char_count']} chars")
        assert len(chunks_meta) >= 4, "Expected at least 4 chunks"

        # 3. Create Note and Index Chunks in pgvector
        print("\n[STEP 3] Persisting Note and Indexing Chunks in pgvector...")
        test_note_id = "note-rag-test-01"
        
        # Clean up if existing
        existing = await db.execute(select(Note).where(Note.id == test_note_id))
        old_note = existing.scalar_one_or_none()
        if old_note:
            await db.delete(old_note)
            await db.commit()

        new_note = Note(
            id=test_note_id,
            title="High-Performance RAG Architecture with PostgreSQL and pgvector",
            content=SAMPLE_DOC_CONTENT,
            category="Architecture",
            tags=["RAG", "pgvector", "PostgreSQL", "Embeddings"]
        )
        db.add(new_note)
        await db.commit()

        # Run indexer
        indexed_chunks = await index_note_chunks(db, test_note_id, SAMPLE_DOC_CONTENT)
        print(f"Successfully indexed {len(indexed_chunks)} chunks in PostgreSQL `document_chunks` table!")

        # Verify chunks stored in DB
        db_chunks = (await db.execute(
            select(DocumentChunk).where(DocumentChunk.note_id == test_note_id)
        )).scalars().all()
        print(f"Verified {len(db_chunks)} chunks stored in database.")
        assert len(db_chunks) == len(indexed_chunks)

        # 4. Test Semantic Vector Retrieval (pgvector <=> distance)
        print("\n[STEP 4] Testing pgvector Vector Cosine Distance Retrieval...")
        queries = [
            "How does HNSW indexing scale vector lookup in logarithmic time?",
            "What is the sliding overlap window configuration for chunking?",
            "What is the embedding dimension used for Gemini?"
        ]

        for q in queries:
            print(f"\nQuery: \"{q}\"")
            retrieved = await retrieve_relevant_chunks(db, query=q, note_id=test_note_id, top_k=2)
            assert len(retrieved) > 0, f"No chunks retrieved for query: {q}"
            top_hit = retrieved[0]
            print(f"  -> Top Hit (Similarity: {top_hit['similarity_score']}): [Section: {top_hit['section']}]")
            print(f"     Excerpt: {top_hit['content'][:140]}...")

        # 5. Test AI Copilot Grounded Answer Generation
        print("\n[STEP 5] Testing AI Copilot Streaming with Grounded RAG Chunks...")
        test_prompt = "Explain in detail how HNSW indexing works in PostgreSQL and why it is better than brute-force scans."
        relevant_chunks = await retrieve_relevant_chunks(db, query=test_prompt, note_id=test_note_id, top_k=3)
        
        token_count = 0
        full_text = ""
        print(f"Streaming answer grounded in {len(relevant_chunks)} retrieved chunks:")
        async for chunk in stream_agent_response(
            prompt=test_prompt,
            active_note=new_note.to_dict(),
            retrieved_chunks=relevant_chunks
        ):
            if chunk.startswith("data: ") and chunk.strip() != "data: [DONE]":
                import json
                try:
                    payload = json.loads(chunk[6:].strip())
                    if payload.get("type") == "token":
                        token = payload.get("content", "")
                        token_count += 1
                        full_text += token
                except Exception:
                    pass

        print(f"\nStreamed {token_count} tokens successfully!")
        print("Generated Grounded Answer Excerpt:")
        print("------------------------------------------------------------------")
        print(full_text[:400] + "...")
        print("------------------------------------------------------------------")
        assert token_count > 10, "Expected at least 10 streamed tokens"

        # 6. Cleanup test note
        print("\n[STEP 6] Testing Cascade Deletion in PostgreSQL...")
        await db.delete(new_note)
        await db.commit()
        remaining_chunks = (await db.execute(
            select(func.count(DocumentChunk.id)).where(DocumentChunk.note_id == test_note_id)
        )).scalar()
        print(f"Remaining chunks after note deletion: {remaining_chunks} (Cascade worked!)")
        assert remaining_chunks == 0

    print("\n==================================================================")
    print("  [SUCCESS] COMPLETE RAG PIPELINE TEST PASSED WITH 0 ERRORS!")
    print("==================================================================")

if __name__ == "__main__":
    asyncio.run(run_rag_test())
