from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime

from app.core.database import get_db
from app.models.execution import Execution, ExecutionStatus
from app.models.agent import Agent
from app.schemas.execution import ExecutionCreate, ExecutionResponse, ExecutionListResponse

router = APIRouter()


@router.get("/", response_model=ExecutionListResponse)
async def list_executions(
    agent_id: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """List all executions with optional filtering."""
    query = db.query(Execution)
    
    if agent_id:
        query = query.filter(Execution.agent_id == agent_id)
    if status:
        query = query.filter(Execution.status == status)
    
    total = query.count()
    executions = query.order_by(Execution.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()
    
    return ExecutionListResponse(
        executions=executions,
        total=total,
        page=page,
        page_size=page_size
    )


@router.post("/", response_model=ExecutionResponse, status_code=201)
async def create_execution(
    execution_data: ExecutionCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Start a new execution."""
    # Verify agent exists
    agent = db.query(Agent).filter(Agent.id == execution_data.agent_id).first()
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    execution = Execution(
        agent_id=execution_data.agent_id,
        status=ExecutionStatus.pending
    )
    db.add(execution)
    db.commit()
    db.refresh(execution)
    
    # TODO: Add background task to execute the agent
    # background_tasks.add_task(run_agent_execution, execution.id, execution_data.inputs)
    
    return execution


@router.get("/{execution_id}", response_model=ExecutionResponse)
async def get_execution(execution_id: str, db: Session = Depends(get_db)):
    """Get execution details."""
    execution = db.query(Execution).filter(Execution.id == execution_id).first()
    if not execution:
        raise HTTPException(status_code=404, detail="Execution not found")
    return execution


@router.delete("/{execution_id}", status_code=204)
async def cancel_execution(execution_id: str, db: Session = Depends(get_db)):
    """Cancel running execution."""
    execution = db.query(Execution).filter(Execution.id == execution_id).first()
    if not execution:
        raise HTTPException(status_code=404, detail="Execution not found")
    
    if execution.status not in [ExecutionStatus.pending, ExecutionStatus.running]:
        raise HTTPException(status_code=400, detail="Execution cannot be cancelled")
    
    execution.status = ExecutionStatus.cancelled
    execution.completed_at = datetime.utcnow()
    db.commit()
    return None


@router.get("/{execution_id}/logs")
async def get_execution_logs(execution_id: str, db: Session = Depends(get_db)):
    """Get execution logs."""
    execution = db.query(Execution).filter(Execution.id == execution_id).first()
    if not execution:
        raise HTTPException(status_code=404, detail="Execution not found")
    
    return {"logs": execution.logs or "No logs available"}


@router.post("/{execution_id}/retry", response_model=ExecutionResponse, status_code=201)
async def retry_execution(execution_id: str, db: Session = Depends(get_db)):
    """Retry a failed execution."""
    original = db.query(Execution).filter(Execution.id == execution_id).first()
    if not original:
        raise HTTPException(status_code=404, detail="Execution not found")
    
    # Create a new execution
    new_execution = Execution(
        agent_id=original.agent_id,
        status=ExecutionStatus.pending
    )
    db.add(new_execution)
    db.commit()
    db.refresh(new_execution)
    return new_execution

