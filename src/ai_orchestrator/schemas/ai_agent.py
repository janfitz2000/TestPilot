from pydantic import BaseModel
from typing import Dict, Any, List, Optional

class TestPlanRequest(BaseModel):
    description: str
    instruments: Optional[List[str]] = None
    requirements: Optional[Dict[str, Any]] = None

class TestPlanResponse(BaseModel):
    test_plan: Dict[str, Any]
    confidence: float
    suggestions: List[str]

class OptimizationRequest(BaseModel):
    current_params: Dict[str, Any]
    objective: str
    constraints: List[str]

class OptimizationResponse(BaseModel):
    optimized_params: Dict[str, Any]
    improvement_estimate: float
    confidence: float