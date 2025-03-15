from datetime import datetime, UTC
from typing import Dict, List, Optional
from pydantic import BaseModel, EmailStr, Field


class User(BaseModel):
    """User model for storage and operations."""
    email: EmailStr
    hashed_password: str
    full_name: Optional[str] = None
    company: Optional[str] = None
    is_active: bool = True
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    clients: List[str] = Field(default_factory=list)
    
    class Config:
        json_schema_extra = {
            "example": {
                "email": "user@example.com",
                "hashed_password": "hashed_password_string",
                "full_name": "John Doe",
                "company": "Acme SEO",
                "is_active": True,
                "created_at": "2023-01-01T00:00:00",
                "updated_at": "2023-01-01T00:00:00",
                "clients": ["client1", "client2"]
            }
        }


class UserStyle(BaseModel):
    """User writing style profile."""
    tone: Optional[str] = None
    sentence_structure: Optional[str] = None
    vocabulary_level: Optional[str] = None
    paragraph_structure: Optional[str] = None
    voice: Optional[str] = None
    rhetorical_devices: Optional[str] = None
    distinctive_patterns: Optional[str] = None
    overall_style: Optional[str] = None
    analyzed_at: datetime = Field(default_factory=lambda: datetime.now(UTC))