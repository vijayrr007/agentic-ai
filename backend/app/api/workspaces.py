from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.models.workspace import Workspace
from app.schemas.workspace import WorkspaceCreate, WorkspaceUpdate, WorkspaceResponse

router = APIRouter()


@router.get("/", response_model=List[WorkspaceResponse])
async def list_workspaces(db: Session = Depends(get_db)):
    """List all workspaces."""
    workspaces = db.query(Workspace).all()
    return workspaces


@router.post("/", response_model=WorkspaceResponse, status_code=201)
async def create_workspace(workspace_data: WorkspaceCreate, db: Session = Depends(get_db)):
    """Create a new workspace."""
    workspace = Workspace(
        name=workspace_data.name,
        description=workspace_data.description
    )
    db.add(workspace)
    db.commit()
    db.refresh(workspace)
    return workspace


@router.get("/{workspace_id}", response_model=WorkspaceResponse)
async def get_workspace(workspace_id: str, db: Session = Depends(get_db)):
    """Get workspace details."""
    workspace = db.query(Workspace).filter(Workspace.id == workspace_id).first()
    if not workspace:
        raise HTTPException(status_code=404, detail="Workspace not found")
    return workspace


@router.put("/{workspace_id}", response_model=WorkspaceResponse)
async def update_workspace(
    workspace_id: str,
    workspace_data: WorkspaceUpdate,
    db: Session = Depends(get_db)
):
    """Update workspace."""
    workspace = db.query(Workspace).filter(Workspace.id == workspace_id).first()
    if not workspace:
        raise HTTPException(status_code=404, detail="Workspace not found")
    
    update_data = workspace_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(workspace, field, value)
    
    db.commit()
    db.refresh(workspace)
    return workspace


@router.delete("/{workspace_id}", status_code=204)
async def delete_workspace(workspace_id: str, db: Session = Depends(get_db)):
    """Delete workspace."""
    workspace = db.query(Workspace).filter(Workspace.id == workspace_id).first()
    if not workspace:
        raise HTTPException(status_code=404, detail="Workspace not found")
    
    db.delete(workspace)
    db.commit()
    return None

