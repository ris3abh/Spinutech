from datetime import datetime
from typing import List, Optional

from app.models.user import User, UserStyle
from app.services.file_service import FileService
from app.utils.security import get_password_hash, verify_password


def create_user(
    email: str, password: str, full_name: Optional[str] = None, company: Optional[str] = None
) -> User:
    """
    Create a new user.
    
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
    # Check if user already exists
    existing_user = get_user_by_email(email)
    if existing_user:
        raise ValueError(f"User with email {email} already exists")
    
    # Create new user
    hashed_password = get_password_hash(password)
    user = User(
        email=email,
        hashed_password=hashed_password,
        full_name=full_name,
        company=company,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    
    # Save user
    FileService.save_user(user)
    
    return user


def get_user_by_email(email: str) -> Optional[User]:
    """
    Get a user by email.
    
    Args:
        email: User's email
        
    Returns:
        User: User object or None if not found
    """
    return FileService.load_user(email)


def authenticate_user(email: str, password: str) -> Optional[User]:
    """
    Authenticate a user by email and password.
    
    Args:
        email: User's email
        password: User's password
        
    Returns:
        User: Authenticated user or None if authentication fails
    """
    user = get_user_by_email(email)
    
    if not user:
        return None
    
    if not verify_password(password, user.hashed_password):
        return None
    
    return user


def update_user(
    email: str, 
    full_name: Optional[str] = None,
    company: Optional[str] = None
) -> Optional[User]:
    """
    Update a user's information.
    
    Args:
        email: User's email
        full_name: Updated full name
        company: Updated company
        
    Returns:
        User: Updated user or None if user not found
    """
    user = get_user_by_email(email)
    
    if not user:
        return None
    
    if full_name is not None:
        user.full_name = full_name
    
    if company is not None:
        user.company = company
    
    user.updated_at = datetime.utcnow()
    
    # Save updated user
    FileService.save_user(user)
    
    return user


def get_user_style(email: str) -> Optional[UserStyle]:
    """
    Get a user's writing style profile.
    
    Args:
        email: User's email
        
    Returns:
        UserStyle: Style profile or None if not found
    """
    return FileService.load_user_style(email)


def save_user_style(email: str, style: UserStyle) -> None:
    """
    Save a user's writing style profile.
    
    Args:
        email: User's email
        style: Style profile to save
    """
    style.analyzed_at = datetime.utcnow()
    FileService.save_user_style(email, style)


def list_user_clients(email: str) -> List[str]:
    """
    List all clients for a user.
    
    Args:
        email: User's email
        
    Returns:
        List[str]: List of client IDs
    """
    return FileService.list_clients(email)