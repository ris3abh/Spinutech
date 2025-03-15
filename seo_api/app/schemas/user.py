from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, EmailStr


class UserBase(BaseModel):
    """Base user schema."""
    email: EmailStr
    full_name: Optional[str] = None
    company: Optional[str] = None


class UserProfile(UserBase):
    """User profile response schema."""
    created_at: datetime
    updated_at: datetime
    clients: List[str] = []


class UserUpdate(BaseModel):
    """User update request schema."""
    full_name: Optional[str] = None
    company: Optional[str] = None


class UserStyleProfile(BaseModel):
    """User writing style profile response schema."""
    tone: Optional[str] = None
    sentence_structure: Optional[str] = None
    vocabulary_level: Optional[str] = None
    paragraph_structure: Optional[str] = None
    voice: Optional[str] = None
    rhetorical_devices: Optional[str] = None
    distinctive_patterns: Optional[str] = None
    overall_style: Optional[str] = None
    analyzed_at: Optional[datetime] = None