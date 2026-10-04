from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

class AiAction(BaseModel):
    type: str = Field(..., json_schema_extra={"example": "ADD_TASKS"}) # ADD_TASKS, INSERT_SUMMARY, VIEW_DOCS
    label: str = Field(..., json_schema_extra={"example": "Add 3 tasks to Kanban"})
    payload: Any

class ChatRequest(BaseModel):
    prompt: str = Field(..., json_schema_extra={"example": "Summarize this note and extract tasks"})
    noteId: Optional[str] = None
    sessionId: Optional[str] = "default"

class ChatMessageCreate(BaseModel):
    sender: str = Field(..., json_schema_extra={"example": "user"}) # 'user' | 'ai'
    text: str = Field(..., json_schema_extra={"example": "Can you summarize this note?"})
    noteId: Optional[str] = None
    sessionId: Optional[str] = "default"
    actions: Optional[List[Dict[str, Any]]] = None
    timestamp: Optional[str] = None

class ChatMessageOut(BaseModel):
    id: str
    userId: Optional[str] = None
    sessionId: str
    noteId: Optional[str] = None
    sender: str
    text: str
    actions: List[Dict[str, Any]] = []
    timestamp: str
    createdAt: Optional[str] = None

class ChatResponse(BaseModel):
    text: str
    actions: List[AiAction] = []
    sender: str = "ai"
    timestamp: str

class ExtractTasksRequest(BaseModel):
    content: str = Field(..., json_schema_extra={"example": "- [ ] Implement cosine distance"})
    noteId: Optional[str] = None
    noteTitle: Optional[str] = None

class HealthResponse(BaseModel):
    status: str
    appName: str
    dbEngine: str
    llmProvider: str
    llmModel: str
    vectorDimension: int
    geminiEmbeddingConfigured: Optional[bool] = False

