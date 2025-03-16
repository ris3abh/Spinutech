from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional
from pydantic import BaseModel, EmailStr, Field


class UserRole(str, Enum):
    """Enumeration of possible user roles."""
    SEO_SPECIALIST = "seo_specialist"
    CONTENT_WRITER = "content_writer"
    ACCOUNT_MANAGER = "account_manager"
    ADMIN = "admin"


class User(BaseModel):
    """User model for storage and operations."""
    email: EmailStr
    hashed_password: str
    full_name: Optional[str] = None
    company: Optional[str] = None
    role: UserRole = UserRole.CONTENT_WRITER
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    clients: List[str] = Field(default_factory=list)
    
    class Config:
        json_schema_extra = {
            "example": {
                "email": "user@example.com",
                "hashed_password": "hashed_password_string",
                "full_name": "John Doe",
                "company": "Acme SEO",
                "role": "content_writer",
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
    analyzed_at: datetime = Field(default_factory=datetime.utcnow)