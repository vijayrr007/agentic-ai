from pydantic import BaseModel, Field
from typing import Optional, Any, Dict
from datetime import datetime
from enum import Enum


class DefinitionType(str, Enum):
    ui = "ui"
    yaml = "yaml"
    code = "code"


class AgentBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    definition_type: DefinitionType = DefinitionType.ui
    definition: Dict[str, Any]


class AgentCreate(AgentBase):
    workspace_id: str


class AgentUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    definition_type: Optional[DefinitionType] = None
    definition: Optional[Dict[str, Any]] = None


class AgentResponse(AgentBase):
    id: str
    workspace_id: str
    version: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class AgentListResponse(BaseModel):
    agents: list[AgentResponse]
    total: int
    page: int
    page_size: int

