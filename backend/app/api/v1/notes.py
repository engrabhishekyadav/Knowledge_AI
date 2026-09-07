import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete

from app.core.database import get_db
from app.models.note import Note
from app.models.user import User
from app.schemas.note import NoteCreate, NoteUpdate, NoteResponse, HybridSearchResponse
from app.services.embedding import generate_embedding
from app.services.hybrid_search import perform_hybrid_search
from app.services.document_parser import parse_document
from app.services.auth import get_current_user
from app.core.config import settings

router = APIRouter(prefix="/notes", tags=["Notes"])

@router.post("/upload", response_model=NoteResponse)
async def upload_document(
    file: UploadFile = File(...),
    category: Optional[str] = Form("Interview Prep"),
    current_user: Optional[User] = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Upload and parse PDF, DOCX, TXT, or Markdown documents.
    Auto-creates note and computes pgvector embeddings for semantic retrieval.
    """
    try:
        file_bytes = await file.read()
        if not file_bytes:
            raise HTTPException(status_code=400, detail="Uploaded file is empty.")

        parsed = parse_document(file_bytes, file.filename)
        note_id = f"note-{uuid.uuid4().hex[:8]}"
        emb = generate_embedding(f"{parsed['title']} {parsed['content']}", settings.VECTOR_DIMENSION)

        new_note = Note(
            id=note_id,
            user_id=current_user.id if current_user else None,
            title=parsed["title"],
            content=parsed["content"],
            category=category or "Interview Prep",
            tags=["Document", parsed["doctype"].split()[0], "InterviewPrep"],
            is_favorite=False,
            embedding=emb
        )
        db.add(new_note)
        await db.commit()
        await db.refresh(new_note)
        return new_note.to_dict()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process document: {str(e)}")

@router.get("", response_model=List[NoteResponse])
async def list_notes(
    category: Optional[str] = None,
    tag: Optional[str] = None,
    current_user: Optional[User] = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    if not current_user:
        return []
    
    stmt = select(Note).where(Note.user_id == current_user.id).order_by(Note.updated_at.desc())
    res = await db.execute(stmt)
    notes = res.scalars().all()
    
    filtered = []
    for n in notes:
        if category and n.category != category:
            continue
        if tag and (not n.tags or tag not in n.tags):
            continue
        filtered.append(n.to_dict())
    return filtered

@router.post("", response_model=NoteResponse)
async def create_note(
    note_in: NoteCreate,
    current_user: Optional[User] = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    note_id = f"note-{uuid.uuid4().hex[:8]}"
    emb = generate_embedding(f"{note_in.title} {note_in.content}", settings.VECTOR_DIMENSION)
    
    new_note = Note(
        id=note_id,
        user_id=current_user.id if current_user else None,
        title=note_in.title,
        content=note_in.content,
        category=note_in.category,
        tags=note_in.tags,
        is_favorite=note_in.isFavorite,
        embedding=emb
    )
    db.add(new_note)
    await db.commit()
    await db.refresh(new_note)
    return new_note.to_dict()

@router.get("/search/hybrid", response_model=List[HybridSearchResponse])
async def search_notes_hybrid(
    q: str = Query(..., description="Query string for hybrid semantic search"),
    weight: float = Query(settings.HYBRID_DEFAULT_WEIGHT, ge=0.0, le=1.0),
    limit: int = Query(10, ge=1, le=50),
    db: AsyncSession = Depends(get_db)
):
    return await perform_hybrid_search(db, q, limit=limit, hybrid_weight=weight)

@router.get("/{note_id}", response_model=NoteResponse)
async def get_note(
    note_id: str,
    db: AsyncSession = Depends(get_db)
):
    stmt = select(Note).where(Note.id == note_id)
    res = await db.execute(stmt)
    note = res.scalar_one_or_none()
    if not note:
        raise HTTPException(status_code=404, detail="Document not found")
    return note.to_dict()

@router.put("/{note_id}", response_model=NoteResponse)
async def update_note(
    note_id: str,
    note_in: NoteUpdate,
    db: AsyncSession = Depends(get_db)
):
    stmt = select(Note).where(Note.id == note_id)
    res = await db.execute(stmt)
    note = res.scalar_one_or_none()
    if not note:
        raise HTTPException(status_code=404, detail="Document not found")

    update_data = note_in.model_dump(exclude_unset=True)
    if "isFavorite" in update_data:
        note.is_favorite = update_data.pop("isFavorite")
    for key, value in update_data.items():
        setattr(note, key, value)

    # Refresh vector embedding
    note.embedding = generate_embedding(f"{note.title} {note.content}", settings.VECTOR_DIMENSION)

    await db.commit()
    await db.refresh(note)
    return note.to_dict()

@router.delete("/{note_id}")
async def delete_note(
    note_id: str,
    db: AsyncSession = Depends(get_db)
):
    stmt = select(Note).where(Note.id == note_id)
    res = await db.execute(stmt)
    note = res.scalar_one_or_none()
    if not note:
        raise HTTPException(status_code=404, detail="Document not found")
    
    await db.delete(note)
    await db.commit()
    return {"status": "success", "message": f"Deleted note {note_id}"}
