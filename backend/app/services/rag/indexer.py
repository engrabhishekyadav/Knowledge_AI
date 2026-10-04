import logging
from typing import List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import delete
from app.models.chunk import DocumentChunk
from app.services.embedding import batch_generate_embeddings
from .chunker import chunk_document_text

logger = logging.getLogger("knowledge_ai.rag.indexer")

async def index_note_chunks(
    db: AsyncSession,
    note_id: str,
    content: str
) -> List[DocumentChunk]:
    """
    Extracts text, splits into chunks, computes dense vector embeddings,
    and stores all chunks in PostgreSQL + pgvector for this note.
    """
    if not content or not content.strip():
        # Remove any existing chunks if content is emptied
        await db.execute(delete(DocumentChunk).where(DocumentChunk.note_id == note_id))
        await db.commit()
        return []

    # 1. Clean up old chunks for this note
    await db.execute(delete(DocumentChunk).where(DocumentChunk.note_id == note_id))

    # 2. Split into semantic chunks
    chunks_meta = chunk_document_text(content)
    if not chunks_meta:
        return []

    chunk_texts = [c["content"] for c in chunks_meta]

    # 3. Generate dense embeddings in batch
    embeddings = await batch_generate_embeddings(chunk_texts)

    # 4. Create DocumentChunk records
    new_chunks = []
    for i, c in enumerate(chunks_meta):
        emb = embeddings[i] if i < len(embeddings) else None
        chunk_obj = DocumentChunk(
            note_id=note_id,
            chunk_index=c["chunk_index"],
            section=c.get("section", "General"),
            content=c["content"],
            embedding=emb
        )
        db.add(chunk_obj)
        new_chunks.append(chunk_obj)

    try:
        await db.commit()
        unembedded = sum(1 for c in new_chunks if c.embedding is None)
        if unembedded > 0:
            logger.warning(
                f"Indexed {len(new_chunks)} chunks for note {note_id}, but {unembedded} chunks have embedding=None "
                "(queued for lexical FTS search & automatic backfill)."
            )
        else:
            logger.info(f"Successfully indexed {len(new_chunks)} pgvector chunks for note: {note_id}")
        return new_chunks
    except Exception as e:
        await db.rollback()
        logger.error(f"Failed to commit chunks for note {note_id}: {e}")
        raise

async def backfill_unembedded_chunks(
    db: AsyncSession,
    batch_size: int = 25
) -> int:
    """
    Background backfill worker: finds document chunks that have embedding IS NULL
    and generates/persists their neural embeddings in controlled batches.
    Returns the count of successfully backfilled chunks.
    """
    from sqlalchemy import select
    stmt = select(DocumentChunk).where(DocumentChunk.embedding.is_(None)).limit(batch_size)
    res = await db.execute(stmt)
    chunks_to_embed = res.scalars().all()

    if not chunks_to_embed:
        return 0

    chunk_texts = [c.content for c in chunks_to_embed]
    embeddings = await batch_generate_embeddings(chunk_texts)

    backfilled_count = 0
    for i, chunk in enumerate(chunks_to_embed):
        if i < len(embeddings) and embeddings[i] is not None:
            chunk.embedding = embeddings[i]
            backfilled_count += 1

    if backfilled_count > 0:
        await db.commit()
        logger.info(f"Backfilled {backfilled_count}/{len(chunks_to_embed)} unembedded chunks.")

    return backfilled_count
