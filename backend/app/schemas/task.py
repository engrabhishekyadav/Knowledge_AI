from typing import List, Optional
from pydantic import BaseModel, Field, ConfigDict

class TaskBase(BaseModel):
    title: str = Field(..., json_schema_extra={"example": "Implement LangGraph tool-calling"})
    description: str = Field(default="", json_schema_extra={"example": "Details on task execution"})
    status: str = Field(default="todo", json_schema_extra={"example": "todo"}) # todo, in_progress, done
    priority: str = Field(default="medium", json_schema_extra={"example": "high"}) # urgent, high, medium, low
    dueDate: Optional[str] = Field(default=None, json_schema_extra={"example": "2026-09-15"})
    linkedNoteId: Optional[str] = Field(default=None, json_schema_extra={"example": "note-1"})
    linkedNoteTitle: Optional[str] = Field(default=None, json_schema_extra={"example": "AI Agent Architecture"})
    tags: List[str] = Field(default_factory=list, json_schema_extra={"example": ["AI", "Feature"]})

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
    status: str = Field(..., json_schema_extra={"example": "done"})

class TaskResponse(TaskBase):
    id: str
    userId: Optional[str] = None
    createdAt: Optional[str] = None
    updatedAt: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

class BatchTasksCreate(BaseModel):
    tasks: List[TaskCreate]

