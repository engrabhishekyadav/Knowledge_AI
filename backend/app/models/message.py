import uuid
from typing import Optional, List, Dict, Any
from sqlalchemy import String, Text, JSON
from sqlalchemy.orm import Mapped, mapped_column
from .base import Base, TimestampMixin

class ChatMessage(Base, TimestampMixin):
    __tablename__ = "chat_messages"

    id: Mapped[str] = mapped_column(String(64), primary_key=True, default=lambda: f"msg-{uuid.uuid4().hex[:8]}")
    session_id: Mapped[str] = mapped_column(String(64), default="default", index=True)
    note_id: Mapped[Optional[str]] = mapped_column(String(64), nullable=True, index=True)
    sender: Mapped[str] = mapped_column(String(16), nullable=False) # 'user' | 'ai'
    text: Mapped[str] = mapped_column(Text, nullable=False)
    actions: Mapped[Optional[List[Dict[str, Any]]]] = mapped_column(JSON, default=list)
    timestamp_str: Mapped[Optional[str]] = mapped_column(String(32), nullable=True)

    def to_dict(self):
        return {
            "id": self.id,
            "sessionId": self.session_id,
            "noteId": self.note_id,
            "sender": self.sender,
            "text": self.text,
            "actions": self.actions or [],
            "timestamp": self.timestamp_str or (self.created_at.strftime("%H:%M") if self.created_at else ""),
            "createdAt": self.created_at.isoformat() if self.created_at else None
        }

