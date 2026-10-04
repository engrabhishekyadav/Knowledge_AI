import pytest
from app.services.rag import chunk_document_text, filter_and_rerank_chunks
from app.services.embedding import generate_fallback_embedding, cosine_similarity
from app.services.nlp_extractor import extract_tasks_from_text

def test_semantic_chunker():
    doc = """# Introduction
This is the intro section explaining the high-level architecture.

## Vector Search
Vector search computes cosine distances between 768-dimensional unit embeddings.

## Key Conclusions
Hybrid search significantly enhances BM25 keyword recall.
"""
    chunks = chunk_document_text(doc, chunk_size=200, chunk_overlap=30)
    assert len(chunks) >= 2
    assert any("Vector Search" in c["section"] for c in chunks)
    assert all("content" in c and len(c["content"]) > 0 for c in chunks)

def test_deterministic_embedding_and_similarity():
    text_a = "fastapi pgvector asynchronous python"
    text_b = "fastapi pgvector async database"
    text_c = "gardening and baking chocolate cake"

    vec_a = generate_fallback_embedding(text_a, 768)
    vec_b = generate_fallback_embedding(text_b, 768)
    vec_c = generate_fallback_embedding(text_c, 768)

    assert len(vec_a) == 768
    sim_ab = cosine_similarity(vec_a, vec_b)
    sim_ac = cosine_similarity(vec_a, vec_c)

    assert sim_ab > sim_ac, f"Related texts ({sim_ab}) should score higher than unrelated ({sim_ac})"

def test_precision_reranker_and_threshold_gate():
    candidates = [
        {
            "chunk_id": "c1",
            "content": "Hierarchical Navigable Small World (HNSW) index computes approximate nearest neighbors in O(log N).",
            "section": "PostgreSQL Indexing",
            "similarity_score": 0.88,
            "rrf_score": 0.03
        },
        {
            "chunk_id": "c2",
            "content": "The weather forecast in Seattle expects light rain tomorrow.",
            "section": "Random Facts",
            "similarity_score": 0.15,
            "rrf_score": 0.005
        }
    ]

    result = filter_and_rerank_chunks(
        query="What is the time complexity of HNSW approximate nearest neighbors?",
        candidate_chunks=candidates,
        min_similarity=0.40,
        top_k=2
    )

    assert result["has_relevant_context"] is True
    assert len(result["chunks"]) == 1
    assert result["chunks"][0]["chunk_id"] == "c1"

def test_nlp_task_extractor():
    text = """
Here are the next steps:
- [ ] Configure PostgreSQL 16 with pgvector extension
- [x] Create project structure
TODO: Implement token refresh workflow
"""
    tasks = extract_tasks_from_text(text, note_id="note-1", note_title="Architecture Doc")
    assert len(tasks) == 2
    titles = [t["title"] for t in tasks]
    assert "Configure PostgreSQL 16 with pgvector extension" in titles
    assert "Implement token refresh workflow" in titles
