from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime


class TemplateBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    definition: Dict[str, Any]
    category: str = Field(..., min_length=1, max_length=100)
    is_public: bool = True


class TemplateCreate(TemplateBase):
    author_workspace_id: str


class TemplateUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    definition: Optional[Dict[str, Any]] = None
    category: Optional[str] = Field(None, min_length=1, max_length=100)
    is_public: Optional[bool] = None


class TemplateResponse(TemplateBase):
    id: str
    author_workspace_id: str
    usage_count: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class TemplateListResponse(BaseModel):
    templates: list[TemplateResponse]
    total: int
    page: int
    page_size: int

