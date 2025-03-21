from datetime import datetime
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field


class ClientPreference(BaseModel):
    """Client preference model for content style and tone."""
    tone: Optional[str] = None
    style_notes: Optional[str] = None
    brand_guidelines: Optional[Dict[str, Any]] = None
    target_audience: Optional[List[str]] = None
    voice_characteristics: Optional[List[str]] = None
    taboo_topics: Optional[List[str]] = None
    competitors: Optional[List[str]] = None
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class Client(BaseModel):
    """Client model for storage and operations."""
    client_id: str
    client_name: str
    industry: Optional[str] = None
    specialist_email: str  # Email of the specialist who manages this client (renamed from owner_email)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    content_types: List[str] = Field(default_factory=lambda: ["articles"])
    
    class Config:
        json_schema_extra = {
            "example": {
                "client_id": "acme-corp",
                "client_name": "Acme Corporation",
                "industry": "Technology",
                "specialist_email": "user@example.com",
                "created_at": "2023-01-01T00:00:00",
                "updated_at": "2023-01-01T00:00:00",
                "content_types": ["articles", "landing_page"]
            }
        }