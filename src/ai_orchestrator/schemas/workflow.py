from pydantic import BaseModel
from typing import Dict, Any, Optional
from datetime import datetime
import uuid

class WorkflowBase(BaseModel):
    name: str
    description: Optional[str] = None
    definition: Dict[str, Any]

class WorkflowCreate(WorkflowBase):
    pass

class WorkflowUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    definition: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None

class WorkflowResponse(WorkflowBase):
    id: uuid.UUID
    version: int
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True