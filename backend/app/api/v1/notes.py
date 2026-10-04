import uuid
import logging
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File, Form, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete

from app.core.database import get_db
from app.models.note import Note
from app.models.user import User
from app.schemas.note import NoteCreate, NoteUpdate, NoteResponse, HybridSearchResponse
from app.services.hybrid_search import perform_hybrid_search
from app.services.document_parser import parse_document
from app.services.auth import get_required_current_user
from app.core.config import settings

from app.services.rag import index_note_chunks, retrieve_relevant_chunks

logger = logging.getLogger("knowledge_ai.notes")
router = APIRouter(prefix="/notes", tags=["Notes"])

@router.post("/upload", response_model=NoteResponse)
async def upload_document(
    file: UploadFile = File(...),
    category: Optional[str] = Form("Interview Prep"),
    current_user: User = Depends(get_required_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Upload and parse PDF, DOCX, TXT, or Markdown documents.
    Enforces maximum upload size and authenticated user ownership.
    """
    try:
        max_size = settings.MAX_UPLOAD_SIZE_BYTES
        file_bytes = bytearray()
        chunk_size = 1024 * 1024  # 1MB buffer

        while chunk := await file.read(chunk_size):
            file_bytes.extend(chunk)
            if len(file_bytes) > max_size:
                raise HTTPException(
                    status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                    detail=f"File exceeds maximum allowed upload size of {max_size // (1024 * 1024)}MB."
                )

        if not file_bytes:
            raise HTTPException(status_code=400, detail="Uploaded file is empty.")

        try:
            parsed = parse_document(bytes(file_bytes), file.filename or "uploaded_doc")
        except ValueError as val_err:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(val_err))

        note_id = f"note-{uuid.uuid4().hex[:8]}"

        new_note = Note(
            id=note_id,
            user_id=current_user.id,
            title=parsed["title"],
            content=parsed["content"],
            category=category or "Interview Prep",
            tags=["Document", parsed["doctype"].split()[0], "InterviewPrep"],
            is_favorite=False,
            embedding=None
        )
        db.add(new_note)
        await db.commit()
        await db.refresh(new_note)

        # Index document chunks into pgvector
        try:
            await index_note_chunks(db, note_id, parsed["content"])
        except Exception as chunk_err:
            logger.warning(f"Could not index document chunks for {note_id}: {chunk_err}")

        return new_note.to_dict()
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to process document upload: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to process document: {str(e)}")

@router.get("", response_model=List[NoteResponse])
async def list_notes(
    category: Optional[str] = None,
    tag: Optional[str] = None,
    limit: Optional[int] = Query(None, ge=1, le=100, description="Max notes to return"),
    offset: Optional[int] = Query(None, ge=0, description="Number of notes to skip"),
    current_user: User = Depends(get_required_current_user),
    db: AsyncSession = Depends(get_db)
):
    stmt = select(Note).where(Note.user_id == current_user.id)
    if category:
        stmt = stmt.where(Note.category == category)
    stmt = stmt.order_by(Note.updated_at.desc())
    if limit is not None:
        stmt = stmt.limit(limit)
    if offset is not None:
        stmt = stmt.offset(offset)

    res = await db.execute(stmt)
    notes = res.scalars().all()
    
    if tag:
        return [n.to_dict() for n in notes if n.tags and tag in n.tags]
    return [n.to_dict() for n in notes]

@router.post("", response_model=NoteResponse)
async def create_note(
    note_in: NoteCreate,
    current_user: User = Depends(get_required_current_user),
    db: AsyncSession = Depends(get_db)
):
    note_id = f"note-{uuid.uuid4().hex[:8]}"
    
    new_note = Note(
        id=note_id,
        user_id=current_user.id,
        title=note_in.title,
        content=note_in.content,
        category=note_in.category,
        tags=note_in.tags,
        is_favorite=note_in.isFavorite,
        embedding=None
    )
    db.add(new_note)
    await db.commit()
    await db.refresh(new_note)

    # Index document chunks into pgvector
    try:
        await index_note_chunks(db, note_id, new_note.content)
    except Exception as e:
        logger.warning(f"Note chunks indexing error for {note_id}: {e}")

    return new_note.to_dict()

@router.get("/rag/search")
async def search_rag_chunks(
    q: str = Query(..., description="Query string to search relevant chunks"),
    note_id: Optional[str] = Query(None, description="Optional note ID to filter"),
    k: int = Query(4, ge=1, le=20),
    current_user: User = Depends(get_required_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Search top-k semantically relevant chunks across user's document(s) using pgvector cosine distance.
    Enforces user isolation to prevent cross-tenant data leakage.
    """
    if note_id:
        res = await db.execute(select(Note).where(Note.id == note_id))
        target_note = res.scalar_one_or_none()
        if not target_note:
            raise HTTPException(status_code=404, detail="Document not found")
        if target_note.user_id != current_user.id:
            raise HTTPException(status_code=403, detail="Not authorized to access chunks for this document")

    chunks = await retrieve_relevant_chunks(db, query=q, user_id=current_user.id, note_id=note_id, top_k=k)
    return {"query": q, "count": len(chunks), "chunks": chunks}

@router.get("/search/hybrid", response_model=List[HybridSearchResponse])
async def search_notes_hybrid(
    q: str = Query(..., description="Query string for hybrid semantic search"),
    weight: float = Query(settings.HYBRID_DEFAULT_WEIGHT, ge=0.0, le=1.0),
    limit: int = Query(10, ge=1, le=50),
    current_user: User = Depends(get_required_current_user),
    db: AsyncSession = Depends(get_db)
):
    return await perform_hybrid_search(db, q, limit=limit, hybrid_weight=weight, user_id=current_user.id)

@router.get("/{note_id}", response_model=NoteResponse)
async def get_note(
    note_id: str,
    current_user: User = Depends(get_required_current_user),
    db: AsyncSession = Depends(get_db)
):
    stmt = select(Note).where(Note.id == note_id)
    res = await db.execute(stmt)
    note = res.scalar_one_or_none()
    if not note:
        raise HTTPException(status_code=404, detail="Document not found")
    if note.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to view this document")
    return note.to_dict()

@router.get("/{note_id}/chunks")
async def get_note_chunks(
    note_id: str,
    current_user: User = Depends(get_required_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Retrieve all indexed pgvector chunks for a specific note.
    """
    note_res = await db.execute(select(Note).where(Note.id == note_id))
    note = note_res.scalar_one_or_none()
    if not note:
        raise HTTPException(status_code=404, detail="Document not found")
    if note.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to access chunks for this document")

    from app.models.chunk import DocumentChunk
    stmt = select(DocumentChunk).where(DocumentChunk.note_id == note_id).order_by(DocumentChunk.chunk_index)
    res = await db.execute(stmt)
    chunks = res.scalars().all()
    return [c.to_dict() for c in chunks]

@router.put("/{note_id}", response_model=NoteResponse)
async def update_note(
    note_id: str,
    note_in: NoteUpdate,
    current_user: User = Depends(get_required_current_user),
    db: AsyncSession = Depends(get_db)
):
    stmt = select(Note).where(Note.id == note_id)
    res = await db.execute(stmt)
    note = res.scalar_one_or_none()
    if not note:
        raise HTTPException(status_code=404, detail="Document not found")
    if note.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to modify this document")

    update_data = note_in.model_dump(exclude_unset=True)
    if "isFavorite" in update_data:
        note.is_favorite = update_data.pop("isFavorite")
    content_changed = "content" in update_data and update_data["content"] != note.content

    for key, value in update_data.items():
        setattr(note, key, value)

    await db.commit()
    await db.refresh(note)

    # Refresh chunks in pgvector if content was modified
    if content_changed:
        try:
            await index_note_chunks(db, note_id, note.content)
        except Exception as chunk_err:
            logger.warning(f"Error updating note chunks on note update: {chunk_err}")

    return note.to_dict()

@router.delete("/{note_id}")
async def delete_note(
    note_id: str,
    current_user: User = Depends(get_required_current_user),
    db: AsyncSession = Depends(get_db)
):
    stmt = select(Note).where(Note.id == note_id)
    res = await db.execute(stmt)
    note = res.scalar_one_or_none()
    if not note:
        raise HTTPException(status_code=404, detail="Document not found")
    if note.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this document")
    
    await db.delete(note)
    await db.commit()
    return {"status": "success", "message": f"Deleted note {note_id}"}
