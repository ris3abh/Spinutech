from datetime import timedelta
from typing import Optional

from app.config import settings
from app.models.user import User
from app.services.user_service import authenticate_user, create_user
from app.utils.security import create_access_token


def login(email: str, password: str) -> Optional[str]:
    """
    Authenticate a user and generate an access token.
    
    Args:
        email: User's email
        password: User's password
        
    Returns:
        str: JWT access token or None if authentication fails
    """
    user = authenticate_user(email, password)
    
    if not user:
        return None
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    return create_access_token(
        subject=user.email, expires_delta=access_token_expires
    )


def register(
    email: str, password: str, full_name: Optional[str] = None, company: Optional[str] = None
) -> User:
    """
    Register a new user.
    
    Args:
        email: User's email
        password: User's password
        full_name: User's full name
        company: User's company
        
    Returns:
        User: Created user
        
    Raises:
        ValueError: If user already exists
    """
    return create_user(email=email, password=password, full_name=full_name, company=company)