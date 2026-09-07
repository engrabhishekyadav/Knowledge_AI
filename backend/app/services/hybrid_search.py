from typing import List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.note import Note
from app.services.embedding import generate_embedding, cosine_similarity
from app.core.config import settings

async def perform_hybrid_search(
    db: AsyncSession,
    query: str,
    limit: int = 10,
    hybrid_weight: float = settings.HYBRID_DEFAULT_WEIGHT
) -> List[Dict[str, Any]]:
    """
    Executes hybrid search combining lexical full-text scoring with vector cosine similarity.
    """
    if not query.strip():
        stmt = select(Note).order_by(Note.updated_at.desc()).limit(limit)
        res = await db.execute(stmt)
        notes = res.scalars().all()
        return [{**note.to_dict(), "matchScore": 1.0, "semanticScore": 1.0, "ftsScore": 1.0} for note in notes]

    # Generate query embedding
    query_vector = generate_embedding(query, settings.VECTOR_DIMENSION)
    query_terms = [t.lower() for t in query.split() if len(t) > 1]

    stmt = select(Note)
    res = await db.execute(stmt)
    all_notes = res.scalars().all()

    scored_results = []

    for note in all_notes:
        # 1. Semantic Similarity Score
        note_embedding = note.embedding or generate_embedding(f"{note.title} {note.content}", settings.VECTOR_DIMENSION)
        semantic_score = cosine_similarity(query_vector, note_embedding)

        # 2. Lexical / Keyword Full-Text Score
        title_lower = note.title.lower()
        content_lower = note.content.lower()
        tags_lower = [t.lower() for t in (note.tags or [])]

        lexical_hits = 0
        for term in query_terms:
            if term in title_lower:
                lexical_hits += 2.0
            if any(term in tag for tag in tags_lower):
                lexical_hits += 1.5
            if term in content_lower:
                lexical_hits += 1.0

        lexical_score = min(lexical_hits / max(len(query_terms) * 2.0, 1.0), 1.0)

        # 3. Hybrid Combined Score
        hybrid_score = (hybrid_weight * semantic_score) + ((1.0 - hybrid_weight) * lexical_score)

        if hybrid_score > 0.05 or lexical_hits > 0:
            scored_results.append({
                **note.to_dict(),
                "matchScore": round(float(hybrid_score), 4),
                "semanticScore": round(float(semantic_score), 4),
                "ftsScore": round(float(lexical_score), 4)
            })

    scored_results.sort(key=lambda x: x["matchScore"], reverse=True)
    return scored_results[:limit]
