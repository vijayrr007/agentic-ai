from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
import uuid

from app.core.database import Base


def generate_uuid():
    return str(uuid.uuid4())


class ServerType(enum.Enum):
    builtin = "builtin"
    custom = "custom"


class TransportType(enum.Enum):
    stdio = "stdio"
    sse = "sse"
    websocket = "websocket"


class MCPServer(Base):
    __tablename__ = "mcp_servers"

    id = Column(String, primary_key=True, default=generate_uuid)
    workspace_id = Column(String, ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(255), nullable=False)
    server_type = Column(SQLEnum(ServerType), nullable=False, default=ServerType.custom)
    transport = Column(SQLEnum(TransportType), nullable=False, default=TransportType.stdio)
    config = Column(JSONB, nullable=False)
    enabled = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    workspace = relationship("Workspace", back_populates="mcp_servers")

