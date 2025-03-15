from datetime import datetime
from typing import Dict, List, Optional
from pydantic import BaseModel, Field


class ContentMetadata(BaseModel):
    """Metadata for content."""
    filename: str
    title: str
    content_type: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    client_id: str
    owner_email: str
    keywords: List[str] = Field(default_factory=list)
    size_bytes: Optional[int] = None
    word_count: Optional[int] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "filename": "article-1.md",
                "title": "How to Improve SEO Rankings",
                "content_type": "article",
                "created_at": "2023-01-01T00:00:00",
                "updated_at": "2023-01-01T00:00:00",
                "client_id": "acme-corp",
                "owner_email": "user@example.com",
                "keywords": ["seo", "rankings", "optimization"],
                "size_bytes": 12345,
                "word_count": 1200
            }
        }


class SEOAnalysisResult(BaseModel):
    """SEO analysis result for content."""
    analyzed_at: datetime = Field(default_factory=datetime.utcnow)
    keyword_density: Dict[str, float] = Field(default_factory=dict)
    recommendations: List[str] = Field(default_factory=list)
    score: Optional[float] = None
    details: Optional[Dict] = None