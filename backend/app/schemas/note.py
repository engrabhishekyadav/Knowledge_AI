from typing import List, Optional
from pydantic import BaseModel, Field, ConfigDict

class NoteBase(BaseModel):
    title: str = Field(..., json_schema_extra={"example": "AI Agent Architecture"})
    content: str = Field(default="", json_schema_extra={"example": "# Notes content"})
    category: str = Field(default="General", json_schema_extra={"example": "Architecture"})
    tags: List[str] = Field(default_factory=list, json_schema_extra={"example": ["AI", "Backend"]})
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
    userId: Optional[str] = None
    createdAt: Optional[str] = None
    updatedAt: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

class HybridSearchResponse(NoteResponse):
    matchScore: float
    semanticScore: Optional[float] = None
    ftsScore: Optional[float] = None

