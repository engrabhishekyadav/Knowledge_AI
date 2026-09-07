from typing import List, Optional
from pydantic import BaseModel, Field

class NoteBase(BaseModel):
    title: str = Field(..., example="AI Agent Architecture")
    content: str = Field(default="", example="# Notes content")
    category: str = Field(default="General", example="Architecture")
    tags: List[str] = Field(default_factory=list, example=["AI", "Backend"])
    isFavorite: bool = Field(default=False)

class NoteCreate(NoteBase):
    pass

class NoteUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    category: Optional[str] = None
    tags: Optional[List[str]] = None
    isFavorite: Optional[bool] = None

class NoteResponse(NoteBase):
    id: str
    createdAt: Optional[str] = None
    updatedAt: Optional[str] = None

    class Config:
        from_attributes = True

class HybridSearchResponse(NoteResponse):
    matchScore: float
    semanticScore: Optional[float] = None
    ftsScore: Optional[float] = None
