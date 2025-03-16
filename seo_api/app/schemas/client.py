from datetime import datetime
from typing import Dict, List, Optional, Any

from pydantic import BaseModel, Field


class ClientBase(BaseModel):
    """Base client schema."""
    client_name: str
    industry: Optional[str] = None
    content_types: Optional[List[str]] = None


class ClientCreate(ClientBase):
    """Client creation request schema."""
    client_id: str


class ClientResponse(ClientBase):
    """Client response schema."""
    client_id: str
    owner_email: str
    created_at: datetime
    updated_at: datetime


class ClientUpdate(BaseModel):
    """Client update request schema."""
    client_name: Optional[str] = None
    industry: Optional[str] = None
    content_types: Optional[List[str]] = None


class ClientPreferenceBase(BaseModel):
    """Base client preference schema."""
    tone: Optional[str] = None
    style_notes: Optional[str] = None
    brand_guidelines: Optional[Dict[str, Any]] = None
    target_audience: Optional[List[str]] = None
    voice_characteristics: Optional[List[str]] = None
    taboo_topics: Optional[List[str]] = None
    competitors: Optional[List[str]] = None


class ClientPreferenceCreate(ClientPreferenceBase):
    """Client preference creation request schema."""
    pass


class ClientPreferenceResponse(ClientPreferenceBase):
    """Client preference response schema."""
    updated_at: datetime


class ClientPreferenceUpdate(ClientPreferenceBase):
    """Client preference update request schema."""
    pass