import logging
import json
from typing import Optional
from fastapi import APIRouter, Depends, Query, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete

from app.core.database import get_db, async_session_factory
from app.models.note import Note
from app.models.user import User
from app.models.message import ChatMessage
from app.schemas.ai import ChatMessageCreate, ExtractTasksRequest
from app.services.agent import stream_agent_response
from app.services.nlp_extractor import extract_tasks_from_text
from app.services.rag import retrieve_relevant_chunks, filter_and_rerank_chunks
from app.services.auth import get_current_user, get_required_current_user, decode_access_token

logger = logging.getLogger("knowledge_ai.ai")
router = APIRouter(prefix="/ai", tags=["AI Copilot"])

@router.get("/rag/retrieve")
async def retrieve_chunks_endpoint(
    query: str = Query(..., description="Search query"),
    note_id: Optional[str] = Query(None, description="Optional Note ID filter"),
    min_similarity: float = Query(0.35, description="Similarity threshold cutoff"),
    top_k: int = Query(4, description="Max chunks to return"),
    current_user: User = Depends(get_required_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Direct endpoint to inspect Feature 1 (Hybrid RRF Retrieval) and Feature 2 (Precision Reranker).
    Enforces user boundaries to prevent cross-tenant chunk retrieval.
    """
    if note_id:
        res = await db.execute(select(Note).where(Note.id == note_id))
        target_note = res.scalar_one_or_none()
        if not target_note:
            raise HTTPException(status_code=404, detail="Document not found")
        if target_note.user_id != current_user.id:
            raise HTTPException(status_code=403, detail="Not authorized to access chunks for this document")

    candidates = await retrieve_relevant_chunks(
        db, query=query, user_id=current_user.id, note_id=note_id, top_k=top_k * 2
    )
    rerank_result = filter_and_rerank_chunks(
        query=query,
        candidate_chunks=candidates,
        min_similarity=min_similarity,
        top_k=top_k
    )
    return rerank_result

@router.get("/chat/history")
async def get_chat_history(
    note_id: Optional[str] = Query(None, description="Note ID to filter messages for"),
    session_id: Optional[str] = Query(None, description="Session ID to filter messages for"),
    limit: int = Query(100, description="Max messages to return"),
    current_user: User = Depends(get_required_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Retrieve stored chat history strictly scoped to the authenticated user.
    """
    if note_id:
        res = await db.execute(select(Note).where(Note.id == note_id))
        target_note = res.scalar_one_or_none()
        if not target_note:
            raise HTTPException(status_code=404, detail="Document not found")
        if target_note.user_id != current_user.id:
            raise HTTPException(status_code=403, detail="Not authorized to access chat history for this document")

    stmt = select(ChatMessage).where(ChatMessage.user_id == current_user.id)
    if note_id:
        stmt = stmt.where(ChatMessage.note_id == note_id)
    elif session_id:
        stmt = stmt.where(ChatMessage.session_id == session_id)
    
    stmt = stmt.order_by(ChatMessage.created_at.asc()).limit(limit)
    res = await db.execute(stmt)
    messages = res.scalars().all()
    return [m.to_dict() for m in messages]

@router.post("/chat/message")
async def save_chat_message(
    msg_data: ChatMessageCreate,
    current_user: User = Depends(get_required_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Save a user or AI chat message strictly associated with the authenticated user.
    """
    if msg_data.noteId:
        res = await db.execute(select(Note).where(Note.id == msg_data.noteId))
        target_note = res.scalar_one_or_none()
        if not target_note:
            raise HTTPException(status_code=404, detail="Document not found")
        if target_note.user_id != current_user.id:
            raise HTTPException(status_code=403, detail="Not authorized to save message to this document")

    new_msg = ChatMessage(
        user_id=current_user.id,
        sender=msg_data.sender,
        text=msg_data.text,
        note_id=msg_data.noteId,
        session_id=msg_data.sessionId or "default",
        actions=msg_data.actions or [],
        timestamp_str=msg_data.timestamp
    )
    db.add(new_msg)
    await db.commit()
    await db.refresh(new_msg)
    return new_msg.to_dict()

@router.delete("/chat/history")
async def clear_chat_history(
    note_id: Optional[str] = Query(None, description="Clear history for specific note"),
    session_id: Optional[str] = Query(None, description="Clear history for specific session"),
    current_user: User = Depends(get_required_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Clear chat history strictly restricted to the authenticated user's messages.
    """
    if note_id:
        res = await db.execute(select(Note).where(Note.id == note_id))
        target_note = res.scalar_one_or_none()
        if not target_note:
            raise HTTPException(status_code=404, detail="Document not found")
        if target_note.user_id != current_user.id:
            raise HTTPException(status_code=403, detail="Not authorized to clear history for this document")

    stmt = delete(ChatMessage).where(ChatMessage.user_id == current_user.id)
    if note_id:
        stmt = stmt.where(ChatMessage.note_id == note_id)
    elif session_id:
        stmt = stmt.where(ChatMessage.session_id == session_id)

    await db.execute(stmt)
    await db.commit()
    return {"message": "Chat history cleared successfully"}

@router.get("/chat/stream")
async def chat_stream(
    prompt: str = Query(..., description="User prompt to AI copilot"),
    note_id: Optional[str] = Query(None, description="Active note ID context"),
    session_id: Optional[str] = Query("default", description="Active session ID"),
    token: Optional[str] = Query(None, description="Authentication token for EventSource/SSE"),
    current_user: Optional[User] = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Streams AI tokens and structured action cards via Server-Sent Events (SSE).
    Auto-persists both user prompt and streamed AI completion to the PostgreSQL database.
    """
    resolved_user = current_user
    if not resolved_user and token:
        payload = decode_access_token(token)
        if payload and "sub" in payload:
            res = await db.execute(select(User).where(User.id == payload["sub"]))
            resolved_user = res.scalar_one_or_none()

    if not resolved_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required for AI Copilot chat streaming.",
            headers={"WWW-Authenticate": "Bearer"}
        )

    active_note = None
    retrieved_chunks = []
    has_relevant_context = True

    if note_id:
        stmt = select(Note).where(Note.id == note_id)
        res = await db.execute(stmt)
        note = res.scalar_one_or_none()
        if not note:
            raise HTTPException(status_code=404, detail="Document not found")
        if note.user_id != resolved_user.id:
            raise HTTPException(status_code=403, detail="Not authorized to access this document context")
        active_note = note.to_dict()

    # Feature 1 & 2: Hybrid RRF Retrieval + Precision Reranking & Similarity Threshold Cutoff
    try:
        candidate_chunks = await retrieve_relevant_chunks(
            db, query=prompt, user_id=resolved_user.id, note_id=note_id, top_k=8
        )
        rerank_result = filter_and_rerank_chunks(
            query=prompt,
            candidate_chunks=candidate_chunks,
            min_similarity=0.35,
            top_k=4
        )
        retrieved_chunks = rerank_result["chunks"]
        has_relevant_context = rerank_result["has_relevant_context"]
    except Exception as rag_err:
        logger.warning(f"RAG retrieval notice: {rag_err}")

    user_id_val = resolved_user.id

    async def persistent_stream_generator():
        # 1. Save the User Prompt to DB
        try:
            async with async_session_factory() as session:
                user_msg = ChatMessage(
                    user_id=user_id_val,
                    sender="user",
                    text=prompt,
                    note_id=note_id,
                    session_id=session_id or "default"
                )
                session.add(user_msg)
                await session.commit()
        except Exception as e:
            logger.warning(f"Failed to persist user prompt to chat history: {e}")

        accumulated_text = ""
        actions_list = []

        # 2. Stream tokens from Agent with RAG grounded chunks
        async for chunk in stream_agent_response(
            prompt=prompt,
            active_note=active_note,
            retrieved_chunks=retrieved_chunks,
            has_relevant_context=has_relevant_context
        ):
            if chunk.startswith("data: ") and chunk.strip() != "data: [DONE]":
                try:
                    payload = json.loads(chunk[6:].strip())
                    if payload.get("type") == "token":
                        accumulated_text += payload.get("content", "")
                    elif payload.get("type") == "action":
                        actions_list.append(payload.get("action"))
                except Exception:
                    pass
            yield chunk

        # 3. Save AI Response & Actions to DB
        if accumulated_text.strip():
            try:
                async with async_session_factory() as session:
                    ai_msg = ChatMessage(
                        user_id=user_id_val,
                        sender="ai",
                        text=accumulated_text,
                        note_id=note_id,
                        session_id=session_id or "default",
                        actions=actions_list
                    )
                    session.add(ai_msg)
                    await session.commit()
            except Exception as e:
                logger.warning(f"Failed to persist AI completion to chat history: {e}")

    return StreamingResponse(
        persistent_stream_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )

@router.post("/extract-tasks")
async def extract_tasks_endpoint(
    req: ExtractTasksRequest
):
    """
    Zero-latency local NLP extraction of checkbox tasks and TODO items.
    """
    extracted = extract_tasks_from_text(
        content=req.content,
        note_id=req.noteId,
        note_title=req.noteTitle
    )
    return {"tasks": extracted, "count": len(extracted)}
