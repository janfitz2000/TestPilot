from fastapi import APIRouter, Depends, HTTPException, Request
from typing import Dict, Any
import logging

from core.ai_client import AIClient
# from core.vector_store import VectorStore  # Temporarily disabled
from schemas.ai_agent import TestPlanRequest, TestPlanResponse, OptimizationRequest

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/ai/generate-test-plan", response_model=TestPlanResponse)
async def generate_test_plan(
    request: TestPlanRequest,
    app_request: Request
):
    """Generate test plan from natural language description"""
    try:
        ai_client: AIClient = app_request.app.state.ai_client
        # vector_store: VectorStore = app_request.app.state.vector_store  # Temporarily disabled
        
        # Retrieve relevant documentation
        # context = await vector_store.search_similar(request.description, limit=5)  # Temporarily disabled
        context = []
        
        # Generate test plan
        test_plan = await ai_client.generate_test_plan(
            description=request.description,
            context=context,
            instruments=request.instruments
        )
        
        logger.info(f"Generated test plan for: {request.description[:50]}...")
        return TestPlanResponse(
            test_plan=test_plan,
            confidence=0.85,  # Placeholder - implement actual confidence scoring
            suggestions=[]  # Placeholder - implement suggestions
        )
    except Exception as e:
        logger.error(f"Failed to generate test plan: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate test plan")

@router.post("/ai/optimize-parameters")
async def optimize_parameters(
    request: OptimizationRequest,
    app_request: Request
):
    """Optimize test parameters using AI"""
    try:
        ai_client: AIClient = app_request.app.state.ai_client
        
        # This is a placeholder - implement actual optimization logic
        optimized_params = await ai_client.optimize_parameters(
            current_params=request.current_params,
            objective=request.objective,
            constraints=request.constraints
        )
        
        logger.info(f"Optimized parameters for objective: {request.objective}")
        return {
            "optimized_params": optimized_params,
            "improvement_estimate": 0.15,  # Placeholder
            "confidence": 0.80  # Placeholder
        }
    except Exception as e:
        logger.error(f"Failed to optimize parameters: {e}")
        raise HTTPException(status_code=500, detail="Failed to optimize parameters")

@router.post("/ai/analyze-failure")
async def analyze_failure(
    failure_data: Dict[str, Any],
    app_request: Request
):
    """Analyze test failure and provide suggestions"""
    try:
        ai_client: AIClient = app_request.app.state.ai_client
        
        analysis = await ai_client.analyze_failure(failure_data)
        
        logger.info("Analyzed test failure")
        return {
            "root_cause": analysis.get("root_cause", "Unknown"),
            "suggestions": analysis.get("suggestions", []),
            "confidence": analysis.get("confidence", 0.5)
        }
    except Exception as e:
        logger.error(f"Failed to analyze failure: {e}")
        raise HTTPException(status_code=500, detail="Failed to analyze failure")