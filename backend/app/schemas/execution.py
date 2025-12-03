from pydantic import BaseModel, Field
from typing import Optional, Any, Dict
from datetime import datetime
from enum import Enum


class ExecutionStatus(str, Enum):
    pending = "pending"
    running = "running"
    completed = "completed"
    failed = "failed"
    cancelled = "cancelled"


class ExecutionCreate(BaseModel):
    agent_id: str
    inputs: Optional[dict] = None
    timeout: Optional[int] = Field(None, gt=0, description="Timeout in seconds")


class ExecutionResponse(BaseModel):
    id: str
    agent_id: str
    status: ExecutionStatus
    input_data: Optional[Dict[str, Any]] = None
    output_data: Optional[Dict[str, Any]] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    logs: Optional[str] = None
    error_message: Optional[str] = None
    created_at: datetime

    model_config = {"from_attributes": True}


class ExecutionListResponse(BaseModel):
    executions: list[ExecutionResponse]
    total: int
    page: int
    page_size: int

