import uuid
from typing import List, Optional
from sqlalchemy import String, Text, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column
from .base import Base, TimestampMixin

class Task(Base, TimestampMixin):
    __tablename__ = "tasks"

    id: Mapped[str] = mapped_column(String(64), primary_key=True, default=lambda: f"task-{uuid.uuid4().hex[:8]}")
    user_id: Mapped[str] = mapped_column(String(64), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False, default="")
    status: Mapped[str] = mapped_column(String(32), default="todo", index=True) # todo, in_progress, done
    priority: Mapped[str] = mapped_column(String(32), default="medium", index=True) # urgent, high, medium, low
    due_date: Mapped[Optional[str]] = mapped_column(String(32), nullable=True)
    
    # Linked Document reference
    linked_note_id: Mapped[Optional[str]] = mapped_column(String(64), ForeignKey("notes.id", ondelete="SET NULL"), nullable=True)
    linked_note_title: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    
    tags: Mapped[List[str]] = mapped_column(JSON, default=list)

    def to_dict(self):
        return {
            "id": self.id,
            "userId": self.user_id,
            "title": self.title,
            "description": self.description,
            "status": self.status,
            "priority": self.priority,
            "dueDate": self.due_date,
            "linkedNoteId": self.linked_note_id,
            "linkedNoteTitle": self.linked_note_title,
            "tags": self.tags or [],
            "createdAt": self.created_at.isoformat() if self.created_at else None,
            "updatedAt": self.updated_at.isoformat() if self.updated_at else None,
        }

