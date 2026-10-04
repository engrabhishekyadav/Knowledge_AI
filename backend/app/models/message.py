import uuid
from typing import Optional, List, Dict, Any
from sqlalchemy import String, Text, JSON, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column
from .base import Base, TimestampMixin

class ChatMessage(Base, TimestampMixin):
    __tablename__ = "chat_messages"

    id: Mapped[str] = mapped_column(String(64), primary_key=True, default=lambda: f"msg-{uuid.uuid4().hex[:8]}")
    user_id: Mapped[str] = mapped_column(String(64), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    session_id: Mapped[str] = mapped_column(String(64), default="default", index=True)
    note_id: Mapped[Optional[str]] = mapped_column(String(64), nullable=True, index=True)
    sender: Mapped[str] = mapped_column(String(16), nullable=False) # 'user' | 'ai'
    text: Mapped[str] = mapped_column(Text, nullable=False)
    actions: Mapped[Optional[List[Dict[str, Any]]]] = mapped_column(JSON, default=list)
    timestamp_str: Mapped[Optional[str]] = mapped_column(String(32), nullable=True)
    tokens_used: Mapped[int] = mapped_column(Integer, default=0)

    def to_dict(self):
        return {
            "id": self.id,
            "userId": self.user_id,
            "sessionId": self.session_id,
            "noteId": self.note_id,
            "sender": self.sender,
            "text": self.text,
            "actions": self.actions or [],
            "tokensUsed": self.tokens_used or 0,
            "timestamp": self.timestamp_str or (self.created_at.strftime("%H:%M") if self.created_at else ""),
            "createdAt": self.created_at.isoformat() if self.created_at else None
        }

