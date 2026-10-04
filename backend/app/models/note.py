import uuid
from typing import List, Optional
from sqlalchemy import String, Text, Boolean, JSON, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import Base, TimestampMixin

class Note(Base, TimestampMixin):
    __tablename__ = "notes"

    id: Mapped[str] = mapped_column(String(64), primary_key=True, default=lambda: f"note-{uuid.uuid4().hex[:8]}")
    user_id: Mapped[str] = mapped_column(String(64), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(255), index=True, nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False, default="")
    category: Mapped[str] = mapped_column(String(64), default="General")
    tags: Mapped[List[str]] = mapped_column(JSON, default=list)
    is_favorite: Mapped[bool] = mapped_column(Boolean, default=False)
    
    # Deprecated: Chunk embeddings in document_chunks are used for native pgvector search
    embedding: Mapped[Optional[List[float]]] = mapped_column(JSON, nullable=True)

    # RAG Chunks
    chunks = relationship("DocumentChunk", back_populates="note", cascade="all, delete-orphan", lazy="selectin")

    def to_dict(self):
        return {
            "id": self.id,
            "userId": self.user_id,
            "title": self.title,
            "content": self.content,
            "category": self.category,
            "tags": self.tags or [],
            "isFavorite": self.is_favorite,
            "updatedAt": self.updated_at.isoformat() if self.updated_at else None,
            "createdAt": self.created_at.isoformat() if self.created_at else None,
        }

