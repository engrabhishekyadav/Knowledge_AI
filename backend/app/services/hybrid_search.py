from typing import List, Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.note import Note
from app.services.rag.retriever import retrieve_relevant_chunks
from app.core.config import settings

async def perform_hybrid_search(
    db: AsyncSession,
    query: str,
    limit: int = 10,
    hybrid_weight: float = settings.HYBRID_DEFAULT_WEIGHT,
    user_id: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    Executes hybrid search across user's knowledge base.
    Uses native pgvector HNSW cosine distance (<=>) and PostgreSQL Full-Text Search (tsvector)
    on document_chunks via Reciprocal Rank Fusion (RRF), aggregating best chunk relevance to notes.
    """
    if not user_id:
        return []

    base_filter = Note.user_id == user_id

    # If query is empty, return latest notes
    if not query.strip():
        stmt = select(Note).where(base_filter).order_by(Note.updated_at.desc()).limit(limit)
        res = await db.execute(stmt)
        notes = res.scalars().all()
        return [{**note.to_dict(), "matchScore": 0.0, "semanticScore": 0.0, "ftsScore": 0.0} for note in notes]

    # 1. Retrieve top matching chunks using native pgvector HNSW + FTS RRF
    candidate_limit = max(limit * 4, 16)
    retrieved_chunks = await retrieve_relevant_chunks(
        db=db,
        query=query,
        user_id=user_id,
        top_k=candidate_limit,
        dense_weight=hybrid_weight,
        sparse_weight=1.0 - hybrid_weight
    )

    # 2. Aggregate best scores per note_id from chunks
    best_chunk_per_note: Dict[str, Dict[str, Any]] = {}
    for chk in retrieved_chunks:
        n_id = chk.get("note_id")
        if not n_id:
            continue
        sim = chk.get("similarity_score", 0.0)
        fts = chk.get("fts_score", 0.0)
        combined = (hybrid_weight * sim) + ((1.0 - hybrid_weight) * min(fts, 1.0))
        
        if n_id not in best_chunk_per_note or combined > best_chunk_per_note[n_id]["matchScore"]:
            best_chunk_per_note[n_id] = {
                "matchScore": round(float(combined), 4),
                "semanticScore": round(float(sim), 4),
                "ftsScore": round(float(fts), 4),
                "section": chk.get("section", "General")
            }

    # 3. Check note titles/tags for direct lexical hits to ensure exact title matches rank high
    query_terms = [t.lower() for t in query.split() if len(t) > 1]
    stmt = select(Note).where(base_filter)
    res = await db.execute(stmt)
    all_user_notes = res.scalars().all()

    scored_notes = []
    for note in all_user_notes:
        chunk_scores = best_chunk_per_note.get(note.id)
        
        # Calculate title and tag lexical match score
        title_lower = note.title.lower()
        tags_lower = [t.lower() for t in (note.tags or [])]
        title_hits = sum(2.0 for term in query_terms if term in title_lower)
        tag_hits = sum(1.5 for term in query_terms if any(term in tag for tag in tags_lower))
        title_tag_score = min((title_hits + tag_hits) / max(len(query_terms) * 2.0, 1.0), 1.0) if query_terms else 0.0

        if chunk_scores:
            base_match = chunk_scores["matchScore"]
            boosted_match = min(1.0, base_match + (0.20 * title_tag_score))
            scored_notes.append({
                **note.to_dict(),
                "matchScore": round(float(boosted_match), 4),
                "semanticScore": chunk_scores["semanticScore"],
                "ftsScore": round(max(chunk_scores["ftsScore"], title_tag_score), 4)
            })
        elif title_tag_score > 0:
            # Note matched on title or tag even if no body chunks matched
            scored_notes.append({
                **note.to_dict(),
                "matchScore": round(float(title_tag_score * (1.0 - hybrid_weight)), 4),
                "semanticScore": 0.0,
                "ftsScore": round(float(title_tag_score), 4)
            })

    scored_notes.sort(key=lambda x: x["matchScore"], reverse=True)
    return scored_notes[:limit]

