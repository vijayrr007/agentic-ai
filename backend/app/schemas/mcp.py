from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime
from enum import Enum


class ServerType(str, Enum):
    builtin = "builtin"
    custom = "custom"


class TransportType(str, Enum):
    stdio = "stdio"
    sse = "sse"
    websocket = "websocket"


class MCPServerBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    server_type: ServerType = ServerType.custom
    transport: TransportType = TransportType.stdio
    config: Dict[str, Any]
    enabled: bool = True


class MCPServerCreate(MCPServerBase):
    workspace_id: str


class MCPServerUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    server_type: Optional[ServerType] = None
    transport: Optional[TransportType] = None
    config: Optional[Dict[str, Any]] = None
    enabled: Optional[bool] = None


class MCPServerResponse(MCPServerBase):
    id: str
    workspace_id: str
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class MCPServerListResponse(BaseModel):
    servers: list[MCPServerResponse]
    total: int


class MCPToolResponse(BaseModel):
    name: str
    description: Optional[str] = None
    schema: Optional[Dict[str, Any]] = None
    server_id: Optional[str] = None

