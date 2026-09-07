from typing import List, Optional
from pydantic import BaseModel, Field

class TaskBase(BaseModel):
    title: str = Field(..., example="Implement LangGraph tool-calling")
    description: str = Field(default="", example="Details on task execution")
    status: str = Field(default="todo", example="todo") # todo, in_progress, done
    priority: str = Field(default="medium", example="high") # urgent, high, medium, low
    dueDate: Optional[str] = Field(default=None, example="2026-09-15")
    linkedNoteId: Optional[str] = Field(default=None, example="note-1")
    linkedNoteTitle: Optional[str] = Field(default=None, example="🧠 AI Agent Architecture")
    tags: List[str] = Field(default_factory=list, example=["AI", "Feature"])

class TaskCreate(TaskBase):
    pass

class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    priority: Optional[str] = None
    dueDate: Optional[str] = None
    linkedNoteId: Optional[str] = None
    linkedNoteTitle: Optional[str] = None
    tags: Optional[List[str]] = None

class TaskStatusUpdate(BaseModel):
    status: str = Field(..., example="done")

class TaskResponse(TaskBase):
    id: str
    createdAt: Optional[str] = None
    updatedAt: Optional[str] = None

    class Config:
        from_attributes = True

class BatchTasksCreate(BaseModel):
    tasks: List[TaskCreate]
