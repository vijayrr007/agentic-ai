from sqlalchemy import Column, String, Text, Boolean, Integer, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB
from datetime import datetime
import uuid

from app.core.database import Base


def generate_uuid():
    return str(uuid.uuid4())


class AgentTemplate(Base):
    __tablename__ = "agent_templates"

    id = Column(String, primary_key=True, default=generate_uuid)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    definition = Column(JSONB, nullable=False)
    category = Column(String(100), nullable=False)
    is_public = Column(Boolean, default=True, nullable=False)
    author_workspace_id = Column(String, ForeignKey("workspaces.id"), nullable=False)
    usage_count = Column(Integer, default=0, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

