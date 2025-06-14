from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # Database
    database_url: str = "postgresql://testpilot:testpilot_dev@localhost:5432/test_automation"
    timescale_url: str = "postgresql://testpilot:testpilot_dev@localhost:5433/timeseries"
    
    # Redis
    redis_url: str = "redis://localhost:6379"
    
    # Message Queue
    nats_url: str = "nats://localhost:4222"
    
    # Vector Store
    vector_store_url: str = "http://localhost:6333"
    
    # AI Configuration
    openai_api_key: Optional[str] = None
    anthropic_api_key: Optional[str] = None
    ai_model_path: Optional[str] = None
    ai_temperature: float = 0.1
    ai_max_tokens: int = 2048
    
    # Security
    jwt_secret_key: str = "your-super-secret-jwt-key-change-this-in-production"
    
    # Application
    debug: bool = False
    log_level: str = "INFO"
    
    class Config:
        env_file = ".env"
        case_sensitive = False

settings = Settings()