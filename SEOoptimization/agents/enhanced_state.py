"""
Enhanced state definition for the content optimization workflow.
This module defines a more detailed state object that includes
client preferences and specialist writing style.
"""

from typing import TypedDict, List, Dict, Any, Optional
from langchain_core.messages import BaseMessage

class EnhancedAgentState(TypedDict):
    """Enhanced state definition for the content optimization workflow."""
    # Input parameters
    topic: str              # Content topic
    tone: str               # Desired writing tone
    length: str             # Desired content length
    keywords: str           # SEO keywords to include
    content_type: str       # Type of content (article, landing_page, journal, success_story)
    
    # Optional inputs
    client_id: Optional[str]       # Client ID for personalization
    specialist_id: Optional[str]   # Specialist ID for style adaptation
    
    # Processing state
    messages: List[BaseMessage]    # Conversation history
    seo_analysis: Optional[Dict[str, Any]]  # SEO analysis results
    client_context: Optional[Dict[str, Any]]  # Client preferences and patterns
    specialist_style: Optional[Dict[str, Any]]  # Specialist writing style analysis
    context_docs: Optional[List[Dict]]  # Relevant documents from knowledge base
    
    # Output state
    content_draft: Optional[str]    # Generated content draft
    adapted_content: Optional[str]  # Style-adapted content
    final_content: Optional[str]    # SEO-optimized content
    validation_report: Optional[Dict[str, Any]]  # Content validation report
    
    # Used for debugging and tracing
    errors: List[str]       # Any errors encountered during processing
    timestamp: str          # Timestamp for when the process started