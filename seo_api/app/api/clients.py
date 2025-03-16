from fastapi import APIRouter, Depends, HTTPException, status
from typing import List

from app.dependencies import get_current_user
from app.models.client import Client, ClientPreference
from app.models.user import User
from app.schemas.client import (
    ClientCreate,
    ClientResponse,
    ClientUpdate,
    ClientPreferenceCreate,
    ClientPreferenceResponse,
    ClientPreferenceUpdate,
)
from app.services.client_service import (
    create_client,
    get_client,
    list_clients,
    update_client,
    get_client_preference,
    save_client_preference,
)

router = APIRouter(prefix="/clients", tags=["clients"])


@router.post("", response_model=ClientResponse, status_code=status.HTTP_201_CREATED)
async def create_new_client(
    client_data: ClientCreate, current_user: User = Depends(get_current_user)
):
    """
    Create a new client for the current user.
    """
    try:
        client = create_client(
            client_id=client_data.client_id,
            client_name=client_data.client_name,
            owner_email=current_user.email,
            industry=client_data.industry,
            content_types=client_data.content_types,
        )
        return client
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("", response_model=List[ClientResponse])
async def read_clients(current_user: User = Depends(get_current_user)):
    """
    Get all clients for the current user.
    """
    return list_clients(current_user.email)


@router.get("/{client_id}", response_model=ClientResponse)
async def read_client(
    client_id: str, current_user: User = Depends(get_current_user)
):
    """
    Get a specific client by ID.
    """
    client = get_client(current_user.email, client_id)
    
    if not client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Client with ID {client_id} not found"
        )
    
    return client


@router.put("/{client_id}", response_model=ClientResponse)
async def update_client_info(
    client_id: str,
    client_data: ClientUpdate,
    current_user: User = Depends(get_current_user)
):
    """
    Update a client's information.
    """
    updated_client = update_client(
        owner_email=current_user.email,
        client_id=client_id,
        client_name=client_data.client_name,
        industry=client_data.industry,
        content_types=client_data.content_types,
    )
    
    if not updated_client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Client with ID {client_id} not found"
        )
    
    return updated_client


@router.get("/{client_id}/preferences", response_model=ClientPreferenceResponse)
async def read_client_preferences(
    client_id: str, current_user: User = Depends(get_current_user)
):
    """
    Get preferences for a specific client.
    """
    # First verify client exists
    client = get_client(current_user.email, client_id)
    
    if not client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Client with ID {client_id} not found"
        )
    
    preferences = get_client_preference(current_user.email, client_id)
    
    if not preferences:
        # Return empty preferences with current timestamp
        preferences = ClientPreference()
    
    return preferences


@router.post("/{client_id}/preferences", response_model=ClientPreferenceResponse)
async def create_client_preferences(
    client_id: str,
    preference_data: ClientPreferenceCreate,
    current_user: User = Depends(get_current_user)
):
    """
    Create or replace preferences for a specific client.
    """
    # First verify client exists
    client = get_client(current_user.email, client_id)
    
    if not client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Client with ID {client_id} not found"
        )
    
    # Create preference object
    preferences = ClientPreference(**preference_data.model_dump())
    
    # Save preferences
    save_client_preference(current_user.email, client_id, preferences)
    
    return preferences


@router.put("/{client_id}/preferences", response_model=ClientPreferenceResponse)
async def update_client_preferences(
    client_id: str,
    preference_data: ClientPreferenceUpdate,
    current_user: User = Depends(get_current_user)
):
    """
    Update preferences for a specific client.
    """
    # First verify client exists
    client = get_client(current_user.email, client_id)
    
    if not client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Client with ID {client_id} not found"
        )
    
    # Get existing preferences
    existing_preferences = get_client_preference(current_user.email, client_id)
    
    if not existing_preferences:
        # Create new preferences if none exist
        existing_preferences = ClientPreference()
    
    # Update preferences with new data, preserving existing values
    update_data = preference_data.model_dump(exclude_unset=True)
    updated_preferences = existing_preferences.model_copy(update=update_data)
    
    # Save updated preferences
    save_client_preference(current_user.email, client_id, updated_preferences)
    
    return updated_preferences