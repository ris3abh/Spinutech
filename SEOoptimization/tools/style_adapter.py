"""
Style adaptation tools for content generation.
This module provides functions to adapt content based on specialist writing style
and client preferences.
"""

from typing import Dict, Any, Optional
from SEOoptimization.models.openai import initialize_llm

def adapt_style_direct(
    content: str,
    specialist_style: Optional[Dict[str, Any]] = None,
    client_context: Optional[Dict[str, Any]] = None
) -> str:
    """
    Adapt content to match specialist writing style and client preferences.
    
    Args:
        content: Original content draft
        specialist_style: Writing style characteristics
        client_context: Client preferences and patterns
        
    Returns:
        Style-adapted content
    """
    if not specialist_style and not client_context:
        print("No style or client context provided, returning original content")
        return content  # No adaptation needed
    
    # Build style guidance
    style_guidance = ""
    
    if specialist_style and isinstance(specialist_style, dict):
        style_guidance += "Writing style to adopt:\n"
        for key, value in specialist_style.items():
            if key != "overall_style" and value and value != "unknown":
                style_guidance += f"- {key.replace('_', ' ').title()}: {value}\n"
        
        # Add overall style if available
        if specialist_style.get("overall_style") and specialist_style["overall_style"] != "unknown":
            style_guidance += f"\nOverall style: {specialist_style['overall_style']}\n"
    
    client_guidance = ""
    if client_context and isinstance(client_context, dict):
        client_guidance += "Client preferences to incorporate:\n"
        
        # Add industry terms
        if client_context.get("industry_terms") and isinstance(client_context["industry_terms"], list):
            terms = client_context["industry_terms"]
            if terms:
                client_guidance += f"- Industry terms to include: {', '.join(terms)}\n"
        
        # Add tone preference
        if client_context.get("tone") and client_context["tone"] != "unknown":
            client_guidance += f"- Preferred tone: {client_context['tone']}\n"
        
        # Add structure preferences
        if client_context.get("structure_preferences") and client_context["structure_preferences"] != "unknown":
            client_guidance += f"- Content structure: {client_context['structure_preferences']}\n"
        
        # Add target audience
        if client_context.get("target_audience") and isinstance(client_context["target_audience"], list):
            audience = client_context["target_audience"]
            if audience:
                client_guidance += f"- Target audience: {', '.join(audience)}\n"
        
        # Add key themes
        if client_context.get("key_themes") and isinstance(client_context["key_themes"], list):
            themes = client_context["key_themes"]
            if themes:
                client_guidance += f"- Key themes to emphasize: {', '.join(themes)}\n"
        
        # Add taboo topics
        if client_context.get("taboo_topics") and isinstance(client_context["taboo_topics"], list):
            taboos = client_context["taboo_topics"]
            if taboos:
                client_guidance += f"- Topics/terms to avoid: {', '.join(taboos)}\n"
        
        # Add competitors
        if client_context.get("competitors") and isinstance(client_context["competitors"], list):
            competitors = client_context["competitors"]
            if competitors:
                client_guidance += f"- Competitors to be aware of: {', '.join(competitors)}\n"
        
        # Add overall analysis
        if client_context.get("overall_analysis") and client_context["overall_analysis"] != "unknown":
            client_guidance += f"\nOverall client approach: {client_context['overall_analysis']}\n"
    
    # Create adaptation prompt
    prompt = f"""
    You are a professional editor specializing in style adaptation.
    Rewrite the following content to match the specified writing style and client preferences,
    while preserving the original message, structure, and SEO value.
    
    IMPORTANT: Maintain all original headers, formatting, and content structure.
    Do not add or remove sections, just adapt the writing style and tone.

    {style_guidance}
    
    {client_guidance}
    
    Original content:
    ```
    {content}
    ```
    
    Adapted content (maintain all headers and formatting, focus only on style adaptation):
    """
    
    # Use LLM for style adaptation
    try:
        llm = initialize_llm(model_name="gpt-4o", temperature=0.3)
        response = llm.invoke(prompt)
        return response.content.strip()
    except Exception as e:
        print(f"Error in style adaptation: {e}")
        return content  # Return original content if adaptation fails