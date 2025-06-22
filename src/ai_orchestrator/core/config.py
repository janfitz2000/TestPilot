import os
from typing import Optional

class Settings:
    def __init__(self):
        # Database Configuration
        self.database_url: str = os.getenv('DATABASE_URL', 'postgresql://testpilot:testpilot_dev@postgres:5432/test_automation')
        self.timescale_url: str = os.getenv('TIMESCALE_URL', 'postgresql://testpilot:testpilot_dev@timescaledb:5432/timeseries')
        self.redis_url: str = os.getenv('REDIS_URL', 'redis://redis:6379')
        self.nats_url: str = os.getenv('NATS_URL', 'nats://nats:4222')
        self.vector_store_url: str = os.getenv('VECTOR_STORE_URL', 'http://qdrant:6333')
        
        # AI Configuration
        self.openai_api_key: Optional[str] = os.getenv('OPENAI_API_KEY')
        self.anthropic_api_key: Optional[str] = os.getenv('ANTHROPIC_API_KEY')
        self.google_api_key: Optional[str] = os.getenv('GOOGLE_API_KEY')
        self.ai_model: str = os.getenv('AI_MODEL_NAME', 'gemini-1.5-pro')
        self.ai_temperature: float = float(os.getenv('AI_TEMPERATURE', '0.1'))
        self.ai_max_tokens: int = int(os.getenv('AI_MAX_TOKENS', '2048'))
        
        # Application
        self.debug: bool = os.getenv('DEBUG', 'false').lower() == 'true'
        self.log_level: str = os.getenv('LOG_LEVEL', 'INFO')

settings = Settings()