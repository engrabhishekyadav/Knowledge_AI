from typing import Optional
from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete

from app.core.database import get_db, async_session_factory
from app.models.note import Note
from app.models.message import ChatMessage
from app.schemas.ai import ChatMessageCreate, ExtractTasksRequest
from app.services.agent import stream_agent_response
from app.services.nlp_extractor import extract_tasks_from_text

router = APIRouter(prefix="/ai", tags=["AI Copilot"])

@router.get("/chat/history")
async def get_chat_history(
    note_id: Optional[str] = Query(None, description="Note ID to filter messages for"),
    session_id: Optional[str] = Query(None, description="Session ID to filter messages for"),
    limit: int = Query(100, description="Max messages to return"),
    db: AsyncSession = Depends(get_db)
):
    """
    Retrieve stored chat history.
    If note_id is provided, returns conversation history for that specific note.
    If session_id is provided, returns conversation history for that session.
    """
    stmt = select(ChatMessage)
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
    db: AsyncSession = Depends(get_db)
):
    """
    Save a user or AI chat message to PostgreSQL database.
    """
    new_msg = ChatMessage(
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
    db: AsyncSession = Depends(get_db)
):
    """
    Clear chat history for a note, session, or all messages.
    """
    stmt = delete(ChatMessage)
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
    db: AsyncSession = Depends(get_db)
):
    """
    Streams AI tokens and structured action cards via Server-Sent Events (SSE).
    Auto-persists both user prompt and streamed AI completion to the PostgreSQL database.
    """
    active_note = None
    if note_id:
        stmt = select(Note).where(Note.id == note_id)
        res = await db.execute(stmt)
        note = res.scalar_one_or_none()
        if note:
            active_note = note.to_dict()

    async def persistent_stream_generator():
        # 1. Save the User Prompt to DB
        try:
            async with async_session_factory() as session:
                user_msg = ChatMessage(
                    sender="user",
                    text=prompt,
                    note_id=note_id,
                    session_id=session_id or "default"
                )
                session.add(user_msg)
                await session.commit()
        except Exception as e:
            pass

        accumulated_text = ""
        actions_list = []

        # 2. Stream tokens from Agent
        async for chunk in stream_agent_response(prompt=prompt, active_note=active_note):
            if chunk.startswith("data: ") and chunk.strip() != "data: [DONE]":
                try:
                    import json
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
                        sender="ai",
                        text=accumulated_text,
                        note_id=note_id,
                        session_id=session_id or "default",
                        actions=actions_list
                    )
                    session.add(ai_msg)
                    await session.commit()
            except Exception as e:
                pass

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
