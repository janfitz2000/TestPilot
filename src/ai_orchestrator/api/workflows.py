from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
import uuid
import logging

from core.database import get_db
from models.workflow import Workflow
from schemas.workflow import WorkflowCreate, WorkflowResponse, WorkflowUpdate

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/workflows", response_model=WorkflowResponse)
async def create_workflow(
    workflow: WorkflowCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create a new workflow"""
    try:
        db_workflow = Workflow(
            id=uuid.uuid4(),
            name=workflow.name,
            description=workflow.description,
            definition=workflow.definition,
            version=1,
            is_active=True
        )
        db.add(db_workflow)
        await db.commit()
        await db.refresh(db_workflow)
        
        logger.info(f"Created workflow: {db_workflow.id}")
        return db_workflow
    except Exception as e:
        logger.error(f"Failed to create workflow: {e}")
        await db.rollback()
        raise HTTPException(status_code=500, detail="Failed to create workflow")

@router.get("/workflows", response_model=List[WorkflowResponse])
async def list_workflows(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    """List all workflows"""
    try:
        workflows = await db.execute(
            "SELECT * FROM workflows WHERE is_active = true ORDER BY created_at DESC LIMIT :limit OFFSET :skip",
            {"limit": limit, "skip": skip}
        )
        return workflows.fetchall()
    except Exception as e:
        logger.error(f"Failed to list workflows: {e}")
        raise HTTPException(status_code=500, detail="Failed to list workflows")

@router.get("/workflows/{workflow_id}", response_model=WorkflowResponse)
async def get_workflow(
    workflow_id: uuid.UUID,
    db: AsyncSession = Depends(get_db)
):
    """Get a specific workflow"""
    try:
        workflow = await db.get(Workflow, workflow_id)
        if not workflow:
            raise HTTPException(status_code=404, detail="Workflow not found")
        return workflow
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get workflow {workflow_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to get workflow")