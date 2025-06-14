from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
from fastapi.responses import Response

from api import health, workflows, ai_agents
from core.config import settings
from core.database import init_db
from core.ai_client import AIClient
from core.vector_store import VectorStore

logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting AI Orchestrator service...")
    
    # Initialize database
    await init_db()
    
    # Initialize AI client
    ai_client = AIClient()
    app.state.ai_client = ai_client
    
    # Initialize vector store
    vector_store = VectorStore()
    await vector_store.initialize()
    app.state.vector_store = vector_store
    
    logger.info("AI Orchestrator service started successfully")
    yield
    
    logger.info("Shutting down AI Orchestrator service...")

app = FastAPI(
    title="TestPilot AI Orchestrator",
    description="AI-powered test workflow orchestration service",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health.router, prefix="/api/v1")
app.include_router(workflows.router, prefix="/api/v1")
app.include_router(ai_agents.router, prefix="/api/v1")

@app.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint"""
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)

@app.get("/")
async def root():
    return {
        "service": "TestPilot AI Orchestrator",
        "version": "1.0.0",
        "status": "running"
    }