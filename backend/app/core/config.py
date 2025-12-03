from typing import List, Optional
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings."""
    
    # API Settings
    API_V1_PREFIX: str = "/api/v1"
    PROJECT_NAME: str = "Agentic AI Platform"
    DEBUG: bool = True
    
    # Database
    DATABASE_URL: str = "postgresql://localhost/agentic_ai"
    
    # CORS
    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost:5173",
        "http://localhost:3000"
    ]
    
    # Authentication
    SECRET_KEY: str = "your-secret-key-change-this-in-production"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # LLM API Keys
    OPENAI_API_KEY: Optional[str] = None
    ANTHROPIC_API_KEY: Optional[str] = None
    HUGGINGFACE_API_KEY: Optional[str] = None
    GOOGLE_API_KEY: Optional[str] = None
    COHERE_API_KEY: Optional[str] = None
    
    # Search API Keys
    SERPAPI_KEY: Optional[str] = None
    BING_SEARCH_API_KEY: Optional[str] = None
    
    # MCP Server Tokens
    GITHUB_TOKEN: Optional[str] = None
    SLACK_TOKEN: Optional[str] = None
    
    # AWS (Optional)
    AWS_ACCESS_KEY_ID: Optional[str] = None
    AWS_SECRET_ACCESS_KEY: Optional[str] = None
    AWS_REGION: str = "us-east-1"
    
    # Google Cloud (Optional)
    GOOGLE_CLOUD_PROJECT: Optional[str] = None
    GOOGLE_APPLICATION_CREDENTIALS: Optional[str] = None
    
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
        extra="ignore"  # Ignore extra env vars not defined here
    )


settings = Settings()

