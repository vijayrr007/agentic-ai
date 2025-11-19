from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional

from app.core.database import get_db
from app.models.template import AgentTemplate
from app.models.agent import Agent
from app.schemas.template import TemplateCreate, TemplateUpdate, TemplateResponse, TemplateListResponse

router = APIRouter()


@router.get("/", response_model=TemplateListResponse)
async def list_templates(
    category: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """List all public templates."""
    query = db.query(AgentTemplate).filter(AgentTemplate.is_public == True)
    
    if category:
        query = query.filter(AgentTemplate.category == category)
    if search:
        query = query.filter(AgentTemplate.name.ilike(f"%{search}%"))
    
    total = query.count()
    templates = query.order_by(AgentTemplate.usage_count.desc()).offset((page - 1) * page_size).limit(page_size).all()
    
    return TemplateListResponse(
        templates=templates,
        total=total,
        page=page,
        page_size=page_size
    )


@router.post("/", response_model=TemplateResponse, status_code=201)
async def create_template(template_data: TemplateCreate, db: Session = Depends(get_db)):
    """Create a new template."""
    template = AgentTemplate(
        name=template_data.name,
        description=template_data.description,
        definition=template_data.definition,
        category=template_data.category,
        is_public=template_data.is_public,
        author_workspace_id=template_data.author_workspace_id
    )
    db.add(template)
    db.commit()
    db.refresh(template)
    return template


@router.get("/{template_id}", response_model=TemplateResponse)
async def get_template(template_id: str, db: Session = Depends(get_db)):
    """Get template details."""
    template = db.query(AgentTemplate).filter(AgentTemplate.id == template_id).first()
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    return template


@router.put("/{template_id}", response_model=TemplateResponse)
async def update_template(
    template_id: str,
    template_data: TemplateUpdate,
    db: Session = Depends(get_db)
):
    """Update template."""
    template = db.query(AgentTemplate).filter(AgentTemplate.id == template_id).first()
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    
    update_data = template_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(template, field, value)
    
    db.commit()
    db.refresh(template)
    return template


@router.delete("/{template_id}", status_code=204)
async def delete_template(template_id: str, db: Session = Depends(get_db)):
    """Delete template."""
    template = db.query(AgentTemplate).filter(AgentTemplate.id == template_id).first()
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    
    db.delete(template)
    db.commit()
    return None


@router.post("/{template_id}/clone", status_code=201)
async def clone_template(
    template_id: str,
    workspace_id: str = Query(...),
    db: Session = Depends(get_db)
):
    """Clone template to workspace."""
    template = db.query(AgentTemplate).filter(AgentTemplate.id == template_id).first()
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    
    # Create agent from template
    agent = Agent(
        workspace_id=workspace_id,
        name=template.name,
        description=template.description,
        definition_type="ui",  # Default to UI type
        definition=template.definition
    )
    db.add(agent)
    
    # Increment usage count
    template.usage_count += 1
    
    db.commit()
    db.refresh(agent)
    return {"message": "Template cloned successfully", "agent_id": agent.id}


@router.get("/categories/list")
async def list_categories(db: Session = Depends(get_db)):
    """Get all template categories."""
    categories = db.query(AgentTemplate.category).distinct().all()
    return {"categories": [cat[0] for cat in categories]}

