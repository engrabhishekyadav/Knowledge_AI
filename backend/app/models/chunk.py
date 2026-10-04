import uuid
from typing import Optional, Dict, Any
from sqlalchemy import String, Text, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from pgvector.sqlalchemy import Vector
from app.core.config import settings
from .base import Base, TimestampMixin

class DocumentChunk(Base, TimestampMixin):
    __tablename__ = "document_chunks"

    id: Mapped[str] = mapped_column(String(64), primary_key=True, default=lambda: f"chk-{uuid.uuid4().hex[:10]}")
    note_id: Mapped[str] = mapped_column(String(64), ForeignKey("notes.id", ondelete="CASCADE"), nullable=False, index=True)
    chunk_index: Mapped[int] = mapped_column(Integer, default=0, index=True)
    section: Mapped[str] = mapped_column(String(255), default="General")
    content: Mapped[str] = mapped_column(Text, nullable=False)
    
    # 768-dimensional dense vector embedding from Gemini
    embedding: Mapped[list] = mapped_column(Vector(settings.VECTOR_DIMENSION), nullable=True)

    note = relationship("Note", back_populates="chunks")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "noteId": self.note_id,
            "chunkIndex": self.chunk_index,
            "section": self.section,
            "content": self.content,
            "createdAt": self.created_at.isoformat() if self.created_at else None,
        }
