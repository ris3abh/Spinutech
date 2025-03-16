"""
API bridge for connecting SEO optimization with external APIs.
This module provides functions to use the SEO optimization pipeline 
from external systems through a clean API.
"""

import sys
import os
import json
from datetime import datetime
from typing import Dict, Any, Optional, List

from SEOoptimization.config.env import load_environment
from SEOoptimization.graphs.enhanced_workflow import run_enhanced_workflow
from SEOoptimization.tools.web_search_enhanced import analyze_keyword_direct
from SEOoptimization.utils.enhanced_knowledge_base import EnhancedKnowledgeBase
from SEOoptimization.utils.file_monitor import get_file_monitor

def generate_content_api(
    topic: str,
    tone: str = "professional",
    length: str = "1000 words",
    keywords: str = "",
    content_type: str = "article",
    client_id: Optional[str] = None,
    specialist_id: Optional[str] = None,
    reference_files: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    API-compatible function to generate content with the enhanced workflow.
    
    Args:
        topic: Content topic
        tone: Desired tone
        length: Content length
        keywords: SEO keywords
        content_type: Type of content (article, landing_page, journal, success_story)
        client_id: Optional client ID for personalization
        specialist_id: Optional specialist ID for style adaptation
        reference_files: Optional list of reference files to include
        
    Returns:
        Dictionary with generated content and analysis
    """
    # Load environment
    load_environment()
    
    # Process any new reference files
    if reference_files:
        kb = EnhancedKnowledgeBase()
        
        for file_path in reference_files:
            if not os.path.exists(file_path):
                print(f"Warning: Reference file not found: {file_path}")
                continue
                
            if '/specialist/' in file_path or '/style_reference/' in file_path:
                # Specialist reference
                if specialist_id:
                    print(f"Adding specialist reference file: {file_path}")
                    kb.add_documents(
                        [file_path],
                        document_type="specialist_reference",
                        owner_id=specialist_id
                    )
                else:
                    print(f"Warning: Missing specialist_id for file: {file_path}")
            else:
                # Client reference
                if client_id and specialist_id:
                    print(f"Adding client reference file: {file_path}")
                    kb.add_documents(
                        [file_path],
                        document_type="client_reference",
                        owner_id=specialist_id,
                        client_id=client_id
                    )
                else:
                    print(f"Warning: Missing client_id or specialist_id for file: {file_path}")
    
    # Validate content_type
    valid_types = ["article", "landing_page", "journal", "success_story"]
    if content_type not in valid_types:
        print(f"Warning: Invalid content_type '{content_type}'. Defaulting to 'article'")
        content_type = "article"
    
    # Run the enhanced workflow
    try:
        result = run_enhanced_workflow(
            topic=topic,
            tone=tone,
            length=length,
            keywords=keywords,
            content_type=content_type,
            client_id=client_id,
            specialist_id=specialist_id
        )
        
        # Format the result for API response
        api_response = {
            "topic": topic,
            "content_type": content_type,
            "seo_analysis": result.get("seo_analysis", {}),
            "client_context": result.get("client_context", {}),
            "specialist_style": result.get("specialist_style", {}),
            "content_draft": result.get("content_draft", ""),
            "adapted_content": result.get("adapted_content", ""),
            "final_content": result.get("final_content", ""),
            "validation_report": result.get("validation_report", {}),
            "messages": [m.content for m in result.get("messages", [])],
            "errors": result.get("errors", []),
            "timestamp": result.get("timestamp", datetime.now().strftime("%Y%m%d%H%M%S"))
        }
        
        return api_response
        
    except Exception as e:
        error_message = f"Error generating content: {str(e)}"
        print(error_message)
        
        # Return error response
        return {
            "topic": topic,
            "content_type": content_type,
            "error": error_message,
            "timestamp": datetime.now().strftime("%Y%m%d%H%M%S")
        }

def analyze_seo_api(
    topic: str,
    keywords: str,
    force_refresh: bool = False
) -> Dict[str, Any]:
    """
    API-compatible function to analyze SEO landscape.
    
    Args:
        topic: Content topic
        keywords: SEO keywords
        force_refresh: Whether to force a fresh analysis
        
    Returns:
        Dictionary with SEO analysis results
    """
    # Load environment
    load_environment()
    
    try:
        # Run the analysis
        seo_analysis = analyze_keyword_direct(
            topic=topic,
            keywords=keywords,
            force_refresh=force_refresh
        )
        
        return seo_analysis
    except Exception as e:
        error_message = f"Error analyzing SEO landscape: {str(e)}"
        print(error_message)
        
        # Return error response
        return {
            "topic": topic,
            "keywords": keywords,
            "error": error_message,
            "timestamp": datetime.now().strftime("%Y%m%d%H%M%S")
        }

def analyze_style_api(
    specialist_id: str,
    file_paths: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    API-compatible function to analyze specialist writing style.
    
    Args:
        specialist_id: Specialist ID
        file_paths: Optional paths to new reference files
        
    Returns:
        Dictionary with writing style analysis
    """
    # Load environment
    load_environment()
    
    try:
        # Initialize knowledge base
        kb = EnhancedKnowledgeBase()
        
        # Add any new files
        if file_paths:
            valid_files = []
            for path in file_paths:
                if os.path.exists(path):
                    valid_files.append(path)
                else:
                    print(f"Warning: File not found: {path}")
            
            if valid_files:
                kb.add_documents(
                    valid_files,
                    document_type="specialist_reference",
                    owner_id=specialist_id
                )
        
        # Analyze writing style
        style_analysis = kb.analyze_writing_style(specialist_id)
        
        # Add timestamp
        style_analysis["timestamp"] = datetime.now().strftime("%Y%m%d%H%M%S")
        style_analysis["specialist_id"] = specialist_id
        
        return style_analysis
    except Exception as e:
        error_message = f"Error analyzing writing style: {str(e)}"
        print(error_message)
        
        # Return error response
        return {
            "specialist_id": specialist_id,
            "error": error_message,
            "timestamp": datetime.now().strftime("%Y%m%d%H%M%S")
        }

def analyze_client_api(
    client_id: str,
    specialist_id: str,
    file_paths: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    API-compatible function to analyze client content patterns.
    
    Args:
        client_id: Client ID
        specialist_id: Specialist ID
        file_paths: Optional paths to new reference files
        
    Returns:
        Dictionary with client content analysis
    """
    # Load environment
    load_environment()
    
    try:
        # Initialize knowledge base
        kb = EnhancedKnowledgeBase()
        
        # Add any new files
        if file_paths:
            valid_files = []
            for path in file_paths:
                if os.path.exists(path):
                    valid_files.append(path)
                else:
                    print(f"Warning: File not found: {path}")
            
            if valid_files:
                kb.add_documents(
                    valid_files,
                    document_type="client_reference",
                    owner_id=specialist_id,
                    client_id=client_id
                )
        
        # Analyze client content
        client_analysis = kb.analyze_client_content(client_id)
        
        # Add metadata
        client_analysis["timestamp"] = datetime.now().strftime("%Y%m%d%H%M%S")
        client_analysis["client_id"] = client_id
        client_analysis["specialist_id"] = specialist_id
        
        return client_analysis
    except Exception as e:
        error_message = f"Error analyzing client content: {str(e)}"
        print(error_message)
        
        # Return error response
        return {
            "client_id": client_id,
            "specialist_id": specialist_id,
            "error": error_message,
            "timestamp": datetime.now().strftime("%Y%m%d%H%M%S")
        }

def start_file_monitoring(data_dir: str = "data") -> bool:
    """
    Start the file monitoring system.
    
    Args:
        data_dir: Directory to monitor for files
        
    Returns:
        True if monitoring started successfully, False otherwise
    """
    try:
        monitor = get_file_monitor(data_dir)
        
        if not monitor.is_running:
            monitor.start()
            return True
        else:
            print("File monitoring is already running")
            return True
    except Exception as e:
        print(f"Error starting file monitoring: {e}")
        return False

def stop_file_monitoring() -> bool:
    """
    Stop the file monitoring system.
    
    Returns:
        True if monitoring stopped successfully, False otherwise
    """
    try:
        monitor = get_file_monitor()
        
        if monitor.is_running:
            monitor.stop()
            return True
        else:
            print("File monitoring is not running")
            return True
    except Exception as e:
        print(f"Error stopping file monitoring: {e}")
        return False