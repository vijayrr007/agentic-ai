from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum


class MessageRole(str, Enum):
    user = "user"
    assistant = "assistant"
    system = "system"


class MessageBase(BaseModel):
    role: MessageRole
    content: str


class MessageCreate(MessageBase):
    pass


class MessageResponse(MessageBase):
    id: str
    conversation_id: str
    created_at: datetime

    model_config = {"from_attributes": True}


class ConversationCreate(BaseModel):
    agent_id: str
    title: Optional[str] = None


class ConversationResponse(BaseModel):
    id: str
    agent_id: str
    title: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    messages: List[MessageResponse] = []

    model_config = {"from_attributes": True}


class ConversationListResponse(BaseModel):
    conversations: List[ConversationResponse]
    total: int
    page: int
    page_size: int


class ChatMessageRequest(BaseModel):
    content: str = Field(..., min_length=1)


class ChatMessageResponse(BaseModel):
    message: MessageResponse
    assistant_message: Optional[MessageResponse] = None


