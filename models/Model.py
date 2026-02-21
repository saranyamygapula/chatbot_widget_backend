from typing import Any, Dict, Literal
from uuid import uuid4

from pydantic import BaseModel, Field


class Message(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    content: str
    additional_kwargs: Dict[str, Any] = {}
    response_metadata: Dict[str, Any] = {}


class AgentContext(BaseModel):
    user_id: str
    org_id: str
    chat_id: str
    language: str | None = None


class ChatRequest(BaseModel):
    language: Literal["english", "spanish"] = "english"
    # details: Dict[str, str]
    user_input: str


class ResumeRequest(BaseModel):
    run_id: str
    response: str
    details: Dict[str, str]
