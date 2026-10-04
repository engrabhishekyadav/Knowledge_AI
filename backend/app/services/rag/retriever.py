import logging
import re
from typing import List, Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, text
from app.models.chunk import DocumentChunk
from app.models.note import Note
from app.services.embedding import generate_dense_embedding, cosine_similarity
from app.core.config import settings
from .chunker import chunk_document_text

logger = logging.getLogger("knowledge_ai.rag.retriever")

async def retrieve_dense_candidates(
    db: AsyncSession,
    query_vector: List[float],
    user_id: Optional[str] = None,
    note_id: Optional[str] = None,
    limit: int = 12
) -> List[Dict[str, Any]]:
    """
    Retrieves dense vector nearest neighbors using pgvector cosine distance (<=>).
    Enforces user_id boundary to prevent cross-tenant document chunk leakage.
    """
    if not note_id and not user_id:
        return []

    try:
        stmt = select(
            DocumentChunk,
            DocumentChunk.embedding.cosine_distance(query_vector).label("distance")
        )
        if note_id:
            if user_id:
                stmt = stmt.join(Note, DocumentChunk.note_id == Note.id).where(
                    DocumentChunk.note_id == note_id,
                    Note.user_id == user_id
                )
            else:
                stmt = stmt.where(DocumentChunk.note_id == note_id)
        elif user_id:
            stmt = stmt.join(Note, DocumentChunk.note_id == Note.id).where(Note.user_id == user_id)

        stmt = stmt.order_by("distance").limit(limit)
        res = await db.execute(stmt)
        rows = res.all()

        results = []
        for rank_idx, (chunk, dist) in enumerate(rows, 1):
            distance_val = dist if dist is not None else 1.0
            similarity = round(max(0.0, min(1.0, 1.0 - distance_val)), 4)
            results.append({
                "chunk": chunk,
                "chunk_id": chunk.id,
                "note_id": chunk.note_id,
                "section": chunk.section,
                "content": chunk.content,
                "similarity_score": similarity,
                "dense_distance": distance_val,
                "dense_rank": rank_idx
            })
        return results
    except Exception as e:
        logger.warning(f"Dense vector retrieval error: {e}")
        return []

async def retrieve_sparse_candidates(
    db: AsyncSession,
    query: str,
    user_id: Optional[str] = None,
    note_id: Optional[str] = None,
    limit: int = 12,
    query_vector: Optional[List[float]] = None
) -> List[Dict[str, Any]]:
    """
    Retrieves sparse lexical keyword matches using PostgreSQL Full-Text Search (tsvector + plainto_tsquery).
    Enforces user_id boundary to prevent cross-tenant document chunk leakage.
    Calculates true cosine similarity against query_vector if provided.
    """
    if not note_id and not user_id:
        return []

    # Sanitize and truncate query for full-text search (limit to 500 chars)
    clean_query = re.sub(r"[^\w\s\-\.]", " ", query[:500]).strip()
    if not clean_query:
        return []

    try:
        ts_vector = func.to_tsvector('english', DocumentChunk.content)
        ts_query = func.plainto_tsquery('english', clean_query)

        stmt = select(
            DocumentChunk,
            func.ts_rank_cd(ts_vector, ts_query).label("fts_rank")
        ).where(
            ts_vector.op("@@")(ts_query)
        )
        if note_id:
            if user_id:
                stmt = stmt.join(Note, DocumentChunk.note_id == Note.id).where(
                    DocumentChunk.note_id == note_id,
                    Note.user_id == user_id
                )
            else:
                stmt = stmt.where(DocumentChunk.note_id == note_id)
        elif user_id:
            stmt = stmt.join(Note, DocumentChunk.note_id == Note.id).where(Note.user_id == user_id)

        stmt = stmt.order_by(text("fts_rank DESC")).limit(limit)
        res = await db.execute(stmt)
        rows = res.all()

        results = []
        for rank_idx, (chunk, fts_rank) in enumerate(rows, 1):
            sim = 0.0
            if query_vector is not None and chunk.embedding is not None:
                try:
                    sim = round(max(0.0, min(1.0, cosine_similarity(query_vector, list(chunk.embedding)))), 4)
                except Exception:
                    sim = 0.0
            elif fts_rank is not None:
                # In pure sparse mode (no query vector), derive a normalized lexical proxy similarity
                sim = round(min(1.0, float(fts_rank) * 2.0), 4)

            results.append({
                "chunk": chunk,
                "chunk_id": chunk.id,
                "note_id": chunk.note_id,
                "section": chunk.section,
                "content": chunk.content,
                "similarity_score": sim,
                "fts_score": round(float(fts_rank), 4) if fts_rank is not None else 0.0,
                "sparse_rank": rank_idx
            })
        return results
    except Exception as e:
        logger.debug(f"Sparse FTS retrieval note: {e}")
        return []

def reciprocal_rank_fusion(
    dense_candidates: List[Dict[str, Any]],
    sparse_candidates: List[Dict[str, Any]],
    dense_weight: float = 0.60,
    sparse_weight: float = 0.40,
    rrf_k: int = 60
) -> List[Dict[str, Any]]:
    """
    Merges dense and sparse search rankings using Reciprocal Rank Fusion (RRF).
    Formula: RRF(d) = sum(w_m / (k + rank_m(d)))
    """
    candidates_by_id: Dict[str, Dict[str, Any]] = {}

    # Process Dense candidates
    for item in dense_candidates:
        c_id = item["chunk_id"]
        dense_rank = item["dense_rank"]
        rrf_contrib = dense_weight / (rrf_k + dense_rank)

        candidates_by_id[c_id] = {
            "chunk_id": c_id,
            "note_id": item["note_id"],
            "section": item["section"],
            "content": item["content"],
            "similarity_score": item["similarity_score"],
            "fts_score": 0.0,
            "dense_rank": dense_rank,
            "sparse_rank": None,
            "rrf_score": rrf_contrib,
            "retrieval_method": "dense_vector"
        }

    # Process Sparse candidates
    for item in sparse_candidates:
        c_id = item["chunk_id"]
        sparse_rank = item["sparse_rank"]
        rrf_contrib = sparse_weight / (rrf_k + sparse_rank)

        if c_id in candidates_by_id:
            # Chunk found in both dense and sparse -> True Hybrid match!
            candidates_by_id[c_id]["rrf_score"] += rrf_contrib
            candidates_by_id[c_id]["sparse_rank"] = sparse_rank
            candidates_by_id[c_id]["fts_score"] = item["fts_score"]
            candidates_by_id[c_id]["retrieval_method"] = "hybrid"
        else:
            candidates_by_id[c_id] = {
                "chunk_id": c_id,
                "note_id": item["note_id"],
                "section": item["section"],
                "content": item["content"],
                "similarity_score": item.get("similarity_score", 0.0),
                "fts_score": item["fts_score"],
                "dense_rank": None,
                "sparse_rank": sparse_rank,
                "rrf_score": rrf_contrib,
                "retrieval_method": "sparse_fts"
            }

    # Sort merged candidates by RRF score descending
    fused_list = list(candidates_by_id.values())
    fused_list.sort(key=lambda x: x["rrf_score"], reverse=True)

    for item in fused_list:
        item["rrf_score"] = round(item["rrf_score"], 6)

    return fused_list

async def retrieve_relevant_chunks(
    db: AsyncSession,
    query: str,
    user_id: Optional[str] = None,
    note_id: Optional[str] = None,
    top_k: int = 6,
    dense_weight: float = 0.60,
    sparse_weight: float = 0.40,
    rrf_k: int = 60
) -> List[Dict[str, Any]]:
    """
    Feature 1: Hybrid Search Architecture
    Executes parallel Dense (pgvector cosine <=> ) and Sparse (PostgreSQL FTS plainto_tsquery) queries,
    then fuses results via Reciprocal Rank Fusion (RRF).
    Enforces user_id boundary to prevent cross-tenant chunk leakage.
    """
    if not query or not query.strip() or (not note_id and not user_id):
        return []

    # 1. Generate query embedding for dense search (with automatic retry)
    query_vector = await generate_dense_embedding(query, settings.VECTOR_DIMENSION)

    # 2. Fetch candidates from search mechanisms with user_id scoping
    candidate_limit = max(top_k * 3, 12)
    dense_candidates = []
    if query_vector is not None:
        dense_candidates = await retrieve_dense_candidates(
            db, query_vector, user_id=user_id, note_id=note_id, limit=candidate_limit
        )
    else:
        logger.info(
            "External embedding API unavailable or unconfigured. "
            "Operating in robust pure Sparse Full-Text Search (FTS) mode."
        )

    sparse_candidates = await retrieve_sparse_candidates(
        db, query, user_id=user_id, note_id=note_id, limit=candidate_limit, query_vector=query_vector
    )

    # 3. Fuse rankings via Reciprocal Rank Fusion
    fused_candidates = reciprocal_rank_fusion(
        dense_candidates=dense_candidates,
        sparse_candidates=sparse_candidates,
        dense_weight=dense_weight,
        sparse_weight=sparse_weight,
        rrf_k=rrf_k
    )

    if fused_candidates:
        logger.info(
            f"Hybrid retrieval retrieved {len(fused_candidates)} fused candidates "
            f"(Dense: {len(dense_candidates)}, Sparse: {len(sparse_candidates)})"
        )
        return fused_candidates[:candidate_limit]

    # 4. Fallback: If note has no chunks indexed yet in DB, chunk on-the-fly
    if note_id:
        stmt = select(Note).where(Note.id == note_id)
        if user_id:
            stmt = stmt.where(Note.user_id == user_id)
        note_res = await db.execute(stmt)
        note = note_res.scalar_one_or_none()
        if note and note.content:
            raw_chunks = chunk_document_text(note.content)
            clean_q_terms = [w.lower() for w in re.findall(r"\b\w{2,}\b", query) if len(w) > 2]
            results = []
            for c in raw_chunks[:top_k]:
                c_content_lower = c["content"].lower()
                c_sec_lower = c["section"].lower()
                hits = sum(1 for term in clean_q_terms if term in c_content_lower or term in c_sec_lower)
                overlap_ratio = hits / max(len(clean_q_terms), 1)

                honest_sim = round(min(1.0, 0.20 + (0.60 * overlap_ratio)), 4) if hits > 0 else 0.0
                results.append({
                    "chunk_id": f"tmp-{c['chunk_index']}",
                    "note_id": note_id,
                    "section": c["section"],
                    "content": c["content"],
                    "similarity_score": honest_sim,
                    "fts_score": round(overlap_ratio, 4),
                    "dense_rank": 1 if hits > 0 else 999,
                    "sparse_rank": None,
                    "rrf_score": round(0.01 * overlap_ratio, 4),
                    "retrieval_method": "on_the_fly"
                })
            return results

    return []
