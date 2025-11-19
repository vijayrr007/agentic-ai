from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional

from app.core.database import get_db
from app.models.agent import Agent
from app.schemas.agent import AgentCreate, AgentUpdate, AgentResponse, AgentListResponse

router = APIRouter()


@router.get("/", response_model=AgentListResponse)
async def list_agents(
    workspace_id: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """List all agents with optional filtering by workspace."""
    query = db.query(Agent)
    
    if workspace_id:
        query = query.filter(Agent.workspace_id == workspace_id)
    
    total = query.count()
    agents = query.offset((page - 1) * page_size).limit(page_size).all()
    
    return AgentListResponse(
        agents=agents,
        total=total,
        page=page,
        page_size=page_size
    )


@router.post("/", response_model=AgentResponse, status_code=201)
async def create_agent(agent_data: AgentCreate, db: Session = Depends(get_db)):
    """Create a new agent."""
    agent = Agent(
        workspace_id=agent_data.workspace_id,
        name=agent_data.name,
        description=agent_data.description,
        definition_type=agent_data.definition_type.value,
        definition=agent_data.definition
    )
    db.add(agent)
    db.commit()
    db.refresh(agent)
    return agent


@router.get("/{agent_id}", response_model=AgentResponse)
async def get_agent(agent_id: str, db: Session = Depends(get_db)):
    """Get agent details."""
    agent = db.query(Agent).filter(Agent.id == agent_id).first()
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    return agent


@router.put("/{agent_id}", response_model=AgentResponse)
async def update_agent(
    agent_id: str,
    agent_data: AgentUpdate,
    db: Session = Depends(get_db)
):
    """Update agent."""
    agent = db.query(Agent).filter(Agent.id == agent_id).first()
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    update_data = agent_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        if field == "definition_type" and value:
            setattr(agent, field, value.value)
        else:
            setattr(agent, field, value)
    
    # Increment version on update
    agent.version += 1
    
    db.commit()
    db.refresh(agent)
    return agent


@router.delete("/{agent_id}", status_code=204)
async def delete_agent(agent_id: str, db: Session = Depends(get_db)):
    """Delete agent."""
    agent = db.query(Agent).filter(Agent.id == agent_id).first()
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    db.delete(agent)
    db.commit()
    return None


@router.post("/{agent_id}/duplicate", response_model=AgentResponse, status_code=201)
async def duplicate_agent(agent_id: str, db: Session = Depends(get_db)):
    """Duplicate an agent."""
    original = db.query(Agent).filter(Agent.id == agent_id).first()
    if not original:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    duplicate = Agent(
        workspace_id=original.workspace_id,
        name=f"{original.name} (Copy)",
        description=original.description,
        definition_type=original.definition_type,
        definition=original.definition
    )
    db.add(duplicate)
    db.commit()
    db.refresh(duplicate)
    return duplicate

