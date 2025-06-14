from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
import redis.asyncio as redis
import httpx
from datetime import datetime
import logging

from core.database import get_db
from core.config import settings

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/health")
async def health_check(db: AsyncSession = Depends(get_db)):
    """Health check endpoint"""
    health_status = {
        "service": "ai-orchestrator",
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "checks": {}
    }
    
    # Database check
    try:
        result = await db.execute(text("SELECT 1"))
        health_status["checks"]["database"] = "healthy"
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        health_status["checks"]["database"] = "unhealthy"
        health_status["status"] = "unhealthy"
    
    # Redis check
    try:
        redis_client = redis.from_url(settings.redis_url)
        await redis_client.ping()
        await redis_client.close()
        health_status["checks"]["redis"] = "healthy"
    except Exception as e:
        logger.error(f"Redis health check failed: {e}")
        health_status["checks"]["redis"] = "unhealthy"
        health_status["status"] = "unhealthy"
    
    # Vector store check
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{settings.vector_store_url}/health")
            if response.status_code == 200:
                health_status["checks"]["vector_store"] = "healthy"
            else:
                health_status["checks"]["vector_store"] = "unhealthy"
                health_status["status"] = "unhealthy"
    except Exception as e:
        logger.error(f"Vector store health check failed: {e}")
        health_status["checks"]["vector_store"] = "unhealthy"
        health_status["status"] = "unhealthy"
    
    return health_status