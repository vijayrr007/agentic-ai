from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks, Request
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime
import traceback
import json
import asyncio
from sse_starlette.sse import EventSourceResponse

from app.core.database import get_db, SessionLocal
from app.models.execution import Execution, ExecutionStatus
from app.models.agent import Agent
from app.schemas.execution import ExecutionCreate, ExecutionResponse, ExecutionListResponse
from app.services.agent_executor import AgentExecutor

router = APIRouter()

# In-memory storage for active execution streams
active_streams = {}  # execution_id -> queue


def run_execution_task(execution_id: str, input_data: Optional[dict] = None):
    """
    Background task to execute an agent.
    
    Args:
        execution_id: ID of the execution to run
        input_data: Input data for the execution
    """
    db = SessionLocal()
    
    # Callback for streaming updates
    def stream_callback(event_type: str, data):
        """Send events to connected SSE clients."""
        if execution_id in active_streams:
            try:
                active_streams[execution_id].put_nowait({
                    "type": event_type,
                    "data": data
                })
            except Exception:
                pass
    
    try:
        # Fetch execution and agent
        execution = db.query(Execution).filter(Execution.id == execution_id).first()
        if not execution:
            return
        
        agent = db.query(Agent).filter(Agent.id == execution.agent_id).first()
        if not agent:
            execution.status = ExecutionStatus.failed
            execution.error_message = "Agent not found"
            execution.completed_at = datetime.utcnow()
            db.commit()
            stream_callback("status", "failed")
            stream_callback("error", "Agent not found")
            return
        
        # Update status to running
        execution.status = ExecutionStatus.running
        execution.started_at = datetime.utcnow()
        execution.input_data = input_data or {}
        db.commit()
        
        # Stream status update
        stream_callback("status", "running")
        
        # Prepare agent definition for executor
        agent_definition = {
            "type": agent.definition_type.value if hasattr(agent.definition_type, 'value') else str(agent.definition_type),
            "tools": agent.definition.get("tools", []),
            "steps": agent.definition.get("steps", [])
        }
        
        # If no steps defined but tools are selected, create a simple step for each tool
        if not agent_definition["steps"] and agent_definition["tools"]:
            # For web_search, use the query from input_data
            if "web_search" in agent_definition["tools"]:
                agent_definition["steps"] = [{
                    "action": "search",
                    "tool": "web_search",
                    "params": {
                        "query": input_data.get("query", "") if input_data else ""
                    }
                }]
        
        # Execute the agent with callback
        executor = AgentExecutor(agent_definition, callback=stream_callback)
        result = executor.execute(inputs=input_data)
        
        # Update execution with results
        if result["status"] == "completed":
            execution.status = ExecutionStatus.completed
            execution.output_data = result.get("results") or result.get("result")
            stream_callback("status", "completed")
        else:
            execution.status = ExecutionStatus.failed
            execution.error_message = result.get("error", "Unknown error")
            stream_callback("status", "failed")
            stream_callback("error", execution.error_message)
        
        execution.logs = result.get("logs", "")
        execution.completed_at = datetime.utcnow()
        db.commit()
        
        # Send completion event
        stream_callback("completed", {
            "status": execution.status.value,
            "output_data": execution.output_data,
            "error_message": execution.error_message
        })
        
    except Exception as e:
        # Handle any unexpected errors
        if execution:
            execution.status = ExecutionStatus.failed
            execution.error_message = str(e)
            execution.logs = traceback.format_exc()
            execution.completed_at = datetime.utcnow()
            db.commit()
            stream_callback("status", "failed")
            stream_callback("error", str(e))
    finally:
        db.close()
        # Clean up stream
        if execution_id in active_streams:
            try:
                active_streams[execution_id].put_nowait({"type": "close", "data": None})
            except Exception:
                pass


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
    
    # Start background execution task
    background_tasks.add_task(run_execution_task, execution.id, execution_data.inputs)
    
    return execution


@router.get("/{execution_id}", response_model=ExecutionResponse)
async def get_execution(execution_id: str, db: Session = Depends(get_db)):
    """Get execution details."""
    execution = db.query(Execution).filter(Execution.id == execution_id).first()
    if not execution:
        raise HTTPException(status_code=404, detail="Execution not found")
    return execution


@router.get("/{execution_id}/stream")
async def stream_execution(execution_id: str, request: Request, db: Session = Depends(get_db)):
    """Stream execution updates via Server-Sent Events."""
    # Verify execution exists
    execution = db.query(Execution).filter(Execution.id == execution_id).first()
    if not execution:
        raise HTTPException(status_code=404, detail="Execution not found")
    
    # Create queue for this execution if it doesn't exist
    if execution_id not in active_streams:
        active_streams[execution_id] = asyncio.Queue()
    
    async def event_generator():
        queue = active_streams[execution_id]
        
        try:
            # Send initial status
            yield {
                "event": "status",
                "data": json.dumps({"status": execution.status.value})
            }
            
            # If execution already completed, send existing data and close
            if execution.status in [ExecutionStatus.completed, ExecutionStatus.failed, ExecutionStatus.cancelled]:
                if execution.logs:
                    for log_line in execution.logs.split('\n'):
                        if log_line.strip():
                            yield {
                                "event": "log",
                                "data": log_line
                            }
                
                yield {
                    "event": "completed",
                    "data": json.dumps({
                        "status": execution.status.value,
                        "output_data": execution.output_data,
                        "error_message": execution.error_message
                    })
                }
                return
            
            # Stream live updates
            while True:
                # Check if client disconnected
                if await request.is_disconnected():
                    break
                
                try:
                    # Wait for event with timeout
                    event = await asyncio.wait_for(queue.get(), timeout=30.0)
                    
                    event_type = event.get("type")
                    event_data = event.get("data")
                    
                    # Close connection if requested
                    if event_type == "close":
                        break
                    
                    # Format data for SSE
                    if event_type == "log":
                        yield {
                            "event": "log",
                            "data": event_data
                        }
                    elif event_type == "status":
                        yield {
                            "event": "status",
                            "data": json.dumps({"status": event_data})
                        }
                    elif event_type == "tool_result":
                        yield {
                            "event": "tool_result",
                            "data": json.dumps(event_data)
                        }
                    elif event_type == "completed":
                        yield {
                            "event": "completed",
                            "data": json.dumps(event_data)
                        }
                        break
                    elif event_type == "error":
                        yield {
                            "event": "error",
                            "data": json.dumps({"error": event_data})
                        }
                        
                except asyncio.TimeoutError:
                    # Send keep-alive ping
                    yield {
                        "event": "ping",
                        "data": json.dumps({"timestamp": datetime.utcnow().isoformat()})
                    }
                    
        finally:
            # Clean up
            if execution_id in active_streams:
                del active_streams[execution_id]
    
    return EventSourceResponse(event_generator())


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

