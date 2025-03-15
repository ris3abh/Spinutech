from datetime import datetime
from typing import List, Optional, Dict, Any

from app.models.client import Client, ClientPreference
from app.services.file_service import FileService


def create_client(
    client_id: str,
    client_name: str,
    specialist_email: str,
    industry: Optional[str] = None,
    content_types: Optional[List[str]] = None
) -> Client:
    """
    Create a new client.
    
    Args:
        client_id: Unique identifier for the client
        client_name: Client's name
        specialist_email: Email of the specialist who manages this client
        industry: Client's industry
        content_types: List of content types for this client
        
    Returns:
        Client: Created client
        
    Raises:
        ValueError: If client already exists
    """
    # Check if client already exists
    existing_client = get_client(specialist_email, client_id)
    if existing_client:
        raise ValueError(f"Client with ID {client_id} already exists for specialist {specialist_email}")
    
    # Set default content types if none provided
    if not content_types:
        content_types = ["articles"]
    
    # Create new client
    client = Client(
        client_id=client_id,
        client_name=client_name,
        specialist_email=specialist_email,
        industry=industry,
        content_types=content_types,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    
    # Save client
    FileService.save_client(client)
    
    return client


def get_client(specialist_email: str, client_id: str) -> Optional[Client]:
    """
    Get a client by specialist email and client ID.
    
    Args:
        specialist_email: Email of the client specialist
        client_id: Client ID
        
    Returns:
        Client: Client object or None if not found
    """
    return FileService.load_client(specialist_email, client_id)


def list_clients(specialist_email: str) -> List[Client]:
    """
    List all clients for a specialist.
    
    Args:
        specialist_email: Email of the client specialist
        
    Returns:
        List[Client]: List of client objects
    """
    client_ids = FileService.list_clients(specialist_email)
    clients = []
    
    for client_id in client_ids:
        client = get_client(specialist_email, client_id)
        if client:
            clients.append(client)
    
    return clients


def update_client(
    specialist_email: str,
    client_id: str,
    client_name: Optional[str] = None,
    industry: Optional[str] = None,
    content_types: Optional[List[str]] = None
) -> Optional[Client]:
    """
    Update a client's information.
    
    Args:
        specialist_email: Email of the client specialist
        client_id: Client ID
        client_name: Updated client name
        industry: Updated industry
        content_types: Updated content types
        
    Returns:
        Client: Updated client or None if client not found
    """
    client = get_client(specialist_email, client_id)
    
    if not client:
        return None
    
    if client_name is not None:
        client.client_name = client_name
    
    if industry is not None:
        client.industry = industry
    
    if content_types is not None:
        client.content_types = content_types
    
    client.updated_at = datetime.utcnow()
    
    # Save updated client
    FileService.save_client(client)
    
    return client


def get_client_preference(specialist_email: str, client_id: str) -> Optional[ClientPreference]:
    """
    Get a client's preferences.
    
    Args:
        specialist_email: Email of the client specialist
        client_id: Client ID
        
    Returns:
        ClientPreference: Preference object or None if not found
    """
    return FileService.load_client_preference(specialist_email, client_id)


def save_client_preference(specialist_email: str, client_id: str, preference: ClientPreference) -> None:
    """
    Save a client's preferences.
    
    Args:
        specialist_email: Email of the client specialist
        client_id: Client ID
        preference: Preference object to save
    """
    preference.updated_at = datetime.utcnow()
    FileService.save_client_preference(specialist_email, client_id, preference)