# SEOoptimization/agents/state.py
from typing import TypedDict, List, Dict, Any, Optional
from langchain_core.messages import BaseMessage

class AgentState(TypedDict):
    """State definition for the SEO optimization workflow.
    
    This state object is passed between nodes in the graph and
    maintains the entire context of the workflow.
    """
    # Input parameters
    topic: str              # Article topic
    tone: str               # Desired writing tone
    length: str             # Desired article length
    keywords: str           # SEO keywords to include
    
    # Processing state
    messages: List[BaseMessage]  # Conversation history
    seo_analysis: Optional[Dict[str, Any]]  # SEO analysis results
    article_draft: Optional[str]  # Generated article draft
    final_article: Optional[str]  # SEO-optimized article
    
    # Used for debugging and tracing
    errors: List[str]       # Any errors encountered during processing