from typing import List, Optional

from pydantic import BaseModel, Field


class ChatMessage(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None
    history: Optional[List[ChatMessage]] = Field(default_factory=list)
    language: Optional[str] = "en"


class ChatResponse(BaseModel):
    reply: str
    session_id: str


class HealthResponse(BaseModel):
    status: str
    message: str
    version: str
