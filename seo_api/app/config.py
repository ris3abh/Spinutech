import os
from pathlib import Path
from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings configuration."""
    
    # API settings
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "SEO Content API"
    
    # JWT settings
    SECRET_KEY: str = Field(default="development_secret_key_change_this_in_production")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30 * 24 * 60  # 30 days
    
    # File storage settings
    BASE_DATA_DIR: Path = Path("data")
    USERS_DIR: Path = Path("data/users")
    
    # SEO Optimization settings
    SEO_PIPELINE_PATH: Optional[Path] = Path("../SEOoptimization")
    
    # OpenAI API key
    OPENAI_API_KEY: Optional[str] = None
    
    # Model config
    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": True,
        "extra": "allow"  # Allow extra fields from .env file
    }


# Create global settings object
settings = Settings()

# Ensure base directories exist
os.makedirs(settings.USERS_DIR, exist_ok=True)