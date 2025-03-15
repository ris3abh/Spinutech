import json
import os
import shutil
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Union, BinaryIO

from app.config import settings
from app.models.client import Client, ClientPreference
from app.models.user import User, UserStyle


class FileService:
    """Service for file system operations."""
    
    @staticmethod
    def get_user_path(email: str) -> Path:
        """Get the path for a user's directory."""
        return settings.USERS_DIR / email
    
    @staticmethod
    def get_client_path(specialist_email: str, client_id: str) -> Path:
        """Get the path for a client's directory."""
        return FileService.get_user_path(specialist_email) / "clients" / client_id
    
    @staticmethod
    def get_content_path(specialist_email: str, client_id: str, content_type: str) -> Path:
        """Get the path for a content type directory."""
        return FileService.get_client_path(specialist_email, client_id) / "content" / content_type
    
    @staticmethod
    def get_user_files_path(specialist_email: str, file_type: str) -> Path:
        """Get the path for a user's files directory."""
        base_path = FileService.get_user_path(specialist_email) / "files"
        path = base_path / file_type
        FileService.ensure_directory(path)
        return path
    
    @staticmethod
    def get_client_files_path(specialist_email: str, client_id: str, file_type: str) -> Path:
        """Get the path for a client's files directory."""
        base_path = FileService.get_client_path(specialist_email, client_id) / "files"
        path = base_path / file_type
        FileService.ensure_directory(path)
        return path
    
    @staticmethod
    def ensure_directory(path: Path) -> None:
        """Ensure a directory exists."""
        os.makedirs(path, exist_ok=True)
    
    @staticmethod
    def save_json(path: Path, data: Dict[str, Any]) -> None:
        """Save data as JSON to a file."""
        FileService.ensure_directory(path.parent)
        with open(path, 'w') as f:
            json.dump(data, f, indent=2, default=str)
    
    @staticmethod
    def load_json(path: Path) -> Optional[Dict[str, Any]]:
        """Load JSON data from a file."""
        if not path.exists():
            return None
        with open(path, 'r') as f:
            return json.load(f)
    
    @staticmethod
    def save_text(path: Path, content: str) -> None:
        """Save text content to a file."""
        FileService.ensure_directory(path.parent)
        with open(path, 'w') as f:
            f.write(content)
    
    @staticmethod
    def load_text(path: Path) -> Optional[str]:
        """Load text content from a file."""
        if not path.exists():
            return None
        with open(path, 'r') as f:
            return f.read()
    
    @staticmethod
    def save_binary_file(path: Path, content: BinaryIO) -> Path:
        """Save binary content to a file."""
        FileService.ensure_directory(path.parent)
        with open(path, 'wb') as buffer:
            shutil.copyfileobj(content, buffer)
        return path
    
    @staticmethod
    def save_user(user: User) -> None:
        """Save a user to the file system."""
        user_path = FileService.get_user_path(user.email)
        FileService.ensure_directory(user_path)
        
        # Create files directories
        for file_type in ["style_reference", "writing_samples"]:
            file_path = user_path / "files" / file_type
            FileService.ensure_directory(file_path)
        
        # Save user profile
        FileService.save_json(user_path / "profile.json", user.model_dump())
    
    @staticmethod
    def load_user(email: str) -> Optional[User]:
        """Load a user from the file system."""
        user_path = FileService.get_user_path(email)
        user_data = FileService.load_json(user_path / "profile.json")
        
        if not user_data:
            return None
            
        return User(**user_data)
    
    @staticmethod
    def save_user_style(email: str, style: UserStyle) -> None:
        """Save a user's writing style to the file system."""
        user_path = FileService.get_user_path(email)
        FileService.ensure_directory(user_path)
        
        # Save style profile
        FileService.save_json(user_path / "style_profile.json", style.model_dump())
    
    @staticmethod
    def load_user_style(email: str) -> Optional[UserStyle]:
        """Load a user's writing style from the file system."""
        user_path = FileService.get_user_path(email)
        style_data = FileService.load_json(user_path / "style_profile.json")
        
        if not style_data:
            return None
            
        return UserStyle(**style_data)
    
    @staticmethod
    def save_client(client: Client) -> None:
        """Save a client to the file system."""
        client_path = FileService.get_client_path(client.specialist_email, client.client_id)
        FileService.ensure_directory(client_path)
        
        # Create content directories
        for content_type in client.content_types:
            content_path = client_path / "content" / content_type
            FileService.ensure_directory(content_path)
        
        # Create files directories
        for file_type in ["reference_content", "brand_guidelines"]:
            file_path = client_path / "files" / file_type
            FileService.ensure_directory(file_path)
        
        # Save client metadata
        FileService.save_json(client_path / "metadata.json", client.model_dump())
        
        # Update user's client list
        user = FileService.load_user(client.specialist_email)
        if user and client.client_id not in user.clients:
            user.clients.append(client.client_id)
            user.updated_at = datetime.utcnow()
            FileService.save_user(user)
    
    @staticmethod
    def load_client(specialist_email: str, client_id: str) -> Optional[Client]:
        """Load a client from the file system."""
        client_path = FileService.get_client_path(specialist_email, client_id)
        client_data = FileService.load_json(client_path / "metadata.json")
        
        if not client_data:
            return None
            
        return Client(**client_data)
    
    @staticmethod
    def list_clients(specialist_email: str) -> List[str]:
        """List all clients for a specialist."""
        user_path = FileService.get_user_path(specialist_email)
        clients_path = user_path / "clients"
        
        if not clients_path.exists():
            return []
            
        return [d.name for d in clients_path.iterdir() if d.is_dir()]
    
    @staticmethod
    def save_client_preference(
        specialist_email: str, client_id: str, preference: ClientPreference
    ) -> None:
        """Save a client's preferences to the file system."""
        client_path = FileService.get_client_path(specialist_email, client_id)
        FileService.ensure_directory(client_path)
        
        # Save preferences
        FileService.save_json(client_path / "preferences.json", preference.model_dump())
    
    @staticmethod
    def load_client_preference(
        specialist_email: str, client_id: str
    ) -> Optional[ClientPreference]:
        """Load a client's preferences from the file system."""
        client_path = FileService.get_client_path(specialist_email, client_id)
        preference_data = FileService.load_json(client_path / "preferences.json")
        
        if not preference_data:
            return None
            
        return ClientPreference(**preference_data)
    
    @staticmethod
    def save_content(
        specialist_email: str, client_id: str, content_type: str, filename: str, content: str
    ) -> None:
        """Save content to the file system."""
        content_path = FileService.get_content_path(specialist_email, client_id, content_type)
        FileService.ensure_directory(content_path)
        
        # Save content
        FileService.save_text(content_path / filename, content)
    
    @staticmethod
    def load_content(
        specialist_email: str, client_id: str, content_type: str, filename: str
    ) -> Optional[str]:
        """Load content from the file system."""
        content_path = FileService.get_content_path(specialist_email, client_id, content_type)
        return FileService.load_text(content_path / filename)
    
    @staticmethod
    def list_content(
        specialist_email: str, client_id: str, content_type: str
    ) -> List[str]:
        """List all content for a client and content type."""
        content_path = FileService.get_content_path(specialist_email, client_id, content_type)
        
        if not content_path.exists():
            return []
            
        return [f.name for f in content_path.iterdir() if f.is_file()]
    
    @staticmethod
    def list_user_files(specialist_email: str, file_type: str) -> List[str]:
        """List all files of a specific type for a user."""
        file_path = FileService.get_user_files_path(specialist_email, file_type)
        
        if not file_path.exists():
            return []
            
        return [f.name for f in file_path.iterdir() if f.is_file()]
    
    @staticmethod
    def list_client_files(specialist_email: str, client_id: str, file_type: str) -> List[str]:
        """List all files of a specific type for a client."""
        file_path = FileService.get_client_files_path(specialist_email, client_id, file_type)
        
        if not file_path.exists():
            return []
            
        return [f.name for f in file_path.iterdir() if f.is_file()]