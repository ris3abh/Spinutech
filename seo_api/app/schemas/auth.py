from typing import Optional
from pydantic import BaseModel, EmailStr
from app.models.user import UserRole


class Token(BaseModel):
    """Token response schema."""
    access_token: str
    token_type: str = "bearer"


class TokenPayload(BaseModel):
    """Token payload schema."""
    sub: Optional[str] = None
    exp: Optional[int] = None


class UserLogin(BaseModel):
    """User login request schema."""
    email: EmailStr
    password: str


class UserCreate(BaseModel):
    """User creation request schema."""
    email: EmailStr
    password: str
    full_name: Optional[str] = None
    company: Optional[str] = None
    role: UserRole = UserRole.CONTENT_WRITER