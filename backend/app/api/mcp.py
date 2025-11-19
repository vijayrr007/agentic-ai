from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional, List

from app.core.database import get_db
from app.models.mcp_config import MCPServer
from app.schemas.mcp import (
    MCPServerCreate, MCPServerUpdate, MCPServerResponse,
    MCPServerListResponse, MCPToolResponse
)

router = APIRouter()


@router.get("/servers", response_model=MCPServerListResponse)
async def list_mcp_servers(
    workspace_id: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """List all MCP servers."""
    query = db.query(MCPServer)
    
    if workspace_id:
        query = query.filter(MCPServer.workspace_id == workspace_id)
    
    servers = query.all()
    return MCPServerListResponse(servers=servers, total=len(servers))


@router.post("/servers", response_model=MCPServerResponse, status_code=201)
async def create_mcp_server(server_data: MCPServerCreate, db: Session = Depends(get_db)):
    """Add a new MCP server."""
    server = MCPServer(
        workspace_id=server_data.workspace_id,
        name=server_data.name,
        server_type=server_data.server_type.value,
        transport=server_data.transport.value,
        config=server_data.config,
        enabled=server_data.enabled
    )
    db.add(server)
    db.commit()
    db.refresh(server)
    return server


@router.get("/servers/{server_id}", response_model=MCPServerResponse)
async def get_mcp_server(server_id: str, db: Session = Depends(get_db)):
    """Get MCP server details."""
    server = db.query(MCPServer).filter(MCPServer.id == server_id).first()
    if not server:
        raise HTTPException(status_code=404, detail="MCP server not found")
    return server


@router.put("/servers/{server_id}", response_model=MCPServerResponse)
async def update_mcp_server(
    server_id: str,
    server_data: MCPServerUpdate,
    db: Session = Depends(get_db)
):
    """Update MCP server configuration."""
    server = db.query(MCPServer).filter(MCPServer.id == server_id).first()
    if not server:
        raise HTTPException(status_code=404, detail="MCP server not found")
    
    update_data = server_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        if field in ["server_type", "transport"] and value:
            setattr(server, field, value.value)
        else:
            setattr(server, field, value)
    
    db.commit()
    db.refresh(server)
    return server


@router.delete("/servers/{server_id}", status_code=204)
async def delete_mcp_server(server_id: str, db: Session = Depends(get_db)):
    """Delete MCP server."""
    server = db.query(MCPServer).filter(MCPServer.id == server_id).first()
    if not server:
        raise HTTPException(status_code=404, detail="MCP server not found")
    
    db.delete(server)
    db.commit()
    return None


@router.post("/servers/{server_id}/test")
async def test_mcp_server(server_id: str, db: Session = Depends(get_db)):
    """Test MCP server connection."""
    server = db.query(MCPServer).filter(MCPServer.id == server_id).first()
    if not server:
        raise HTTPException(status_code=404, detail="MCP server not found")
    
    # TODO: Implement actual MCP connection test
    return {
        "status": "success",
        "message": "MCP server connection test - to be implemented"
    }


@router.post("/servers/{server_id}/enable", response_model=MCPServerResponse)
async def enable_mcp_server(server_id: str, db: Session = Depends(get_db)):
    """Enable MCP server."""
    server = db.query(MCPServer).filter(MCPServer.id == server_id).first()
    if not server:
        raise HTTPException(status_code=404, detail="MCP server not found")
    
    server.enabled = True
    db.commit()
    db.refresh(server)
    return server


@router.post("/servers/{server_id}/disable", response_model=MCPServerResponse)
async def disable_mcp_server(server_id: str, db: Session = Depends(get_db)):
    """Disable MCP server."""
    server = db.query(MCPServer).filter(MCPServer.id == server_id).first()
    if not server:
        raise HTTPException(status_code=404, detail="MCP server not found")
    
    server.enabled = False
    db.commit()
    db.refresh(server)
    return server


@router.get("/servers/{server_id}/tools", response_model=List[MCPToolResponse])
async def list_server_tools(server_id: str, db: Session = Depends(get_db)):
    """List available tools from an MCP server."""
    server = db.query(MCPServer).filter(MCPServer.id == server_id).first()
    if not server:
        raise HTTPException(status_code=404, detail="MCP server not found")
    
    # TODO: Implement actual tool discovery from MCP server
    return []


@router.get("/builtin", response_model=List[MCPToolResponse])
async def list_builtin_tools():
    """List built-in MCP tools."""
    # Placeholder for built-in tools
    builtin_tools = [
        MCPToolResponse(
            name="web_search",
            description="Search the web for information",
            schema={"query": "string"}
        ),
        MCPToolResponse(
            name="file_read",
            description="Read a file from disk",
            schema={"path": "string"}
        ),
        MCPToolResponse(
            name="file_write",
            description="Write content to a file",
            schema={"path": "string", "content": "string"}
        ),
        MCPToolResponse(
            name="http_request",
            description="Make an HTTP request",
            schema={"url": "string", "method": "string", "body": "object"}
        )
    ]
    return builtin_tools


@router.get("/tools", response_model=List[MCPToolResponse])
async def list_all_tools(
    workspace_id: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """List all available MCP tools (built-in + configured servers)."""
    # Start with built-in tools
    tools = await list_builtin_tools()
    
    # TODO: Add tools from configured servers
    
    return tools


@router.post("/tools/call")
async def call_mcp_tool(
    tool_name: str = Query(...),
    server_id: Optional[str] = Query(None),
    params: dict = {}
):
    """Execute a specific MCP tool."""
    # TODO: Implement actual MCP tool execution
    return {
        "status": "success",
        "message": f"MCP tool '{tool_name}' execution - to be implemented",
        "result": None
    }

