from fastapi import APIRouter, Depends, HTTPException, status

from app.dependencies import get_current_user
from app.models.user import User
from app.schemas.user import UserProfile, UserUpdate, UserStyleProfile
from app.services.user_service import get_user_style, list_user_clients, update_user

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=UserProfile)
async def read_users_me(current_user: User = Depends(get_current_user)):
    """
    Get current user profile.
    """
    return current_user


@router.put("/me", response_model=UserProfile)
async def update_user_profile(
    user_update: UserUpdate, current_user: User = Depends(get_current_user)
):
    """
    Update current user profile.
    """
    updated_user = update_user(
        email=current_user.email,
        full_name=user_update.full_name,
        company=user_update.company
    )
    
    if not updated_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return updated_user


@router.get("/me/style", response_model=UserStyleProfile)
async def read_user_style(current_user: User = Depends(get_current_user)):
    """
    Get current user's writing style profile.
    """
    style = get_user_style(current_user.email)
    
    if not style:
        return UserStyleProfile()
    
    return style


@router.get("/me/clients", response_model=list[str])
async def read_user_clients(current_user: User = Depends(get_current_user)):
    """
    Get list of clients for current user.
    """
    return list_user_clients(current_user.email)