"""
Content generation tools for different content types.
This module provides functions to generate various types of content
with SEO optimization and client context integration.
"""

from typing import Dict, Any, Optional, List
from SEOoptimization.models.openai import initialize_llm

def get_content_structure(content_type: str) -> str:
    """
    Get structure guidance based on content type.
    
    Args:
        content_type: Type of content (article, landing_page, journal, success_story)
        
    Returns:
        String with structure guidance
    """
    structures = {
        "article": """
        Structure the article with:
        - Catchy title that includes main keywords
        - Introduction that hooks the reader and includes primary keywords
        - 3-5 main sections with appropriate headings (use ## for section headings)
        - Conclusion with a clear call to action
        - Meta description for SEO (include at the end with <!-- Meta: ... -->)
        """,
        
        "landing_page": """
        Structure the landing page with:
        - Attention-grabbing headline with primary keyword (use # for the headline)
        - Subheadline explaining the value proposition (use ## for subheadline)
        - 3-4 benefit sections with icons/visuals placeholders (use ### for benefit headings)
        - Testimonial section placeholders (use ### for testimonial heading)
        - Clear call-to-action sections (use ### for CTA heading)
        - FAQ section addressing common concerns (use ### for FAQ heading and #### for each question)
        """,
        
        "journal": """
        Structure the journal entry with:
        - Scholarly title including primary keywords (use # for title)
        - Abstract summarizing key findings (use ## for Abstract heading)
        - Introduction with context and background (use ## for Introduction heading)
        - Methodology section if applicable (use ## for Methodology heading)
        - Findings/Results with supporting evidence (use ## for Findings heading)
        - Discussion and analysis (use ## for Discussion heading)
        - Conclusion with implications (use ## for Conclusion heading)
        - References section placeholder (use ## for References heading)
        """,
        
        "success_story": """
        Structure the success story with:
        - Compelling title with client name and achievement (use # for title)
        - Executive summary highlighting key results (use ## for Executive Summary heading)
        - Challenge section explaining the problem (use ## for Challenge heading)
        - Solution section detailing the approach (use ## for Solution heading)
        - Results section with specific metrics and outcomes (use ## for Results heading)
        - Client testimonial placeholder (use ## for Testimonial heading)
        - Call to action for similar solutions (use ## for Next Steps heading)
        """
    }
    
    return structures.get(content_type, structures["article"])

def generate_content_direct(
    topic: str,
    tone: str,
    length: str,
    keywords: str,
    content_type: str = "article",
    context: Optional[Dict[str, Any]] = None,
    existing_content: Optional[str] = None
) -> str:
    """
    Generate content based on type and available context.
    
    Args:
        topic: Content topic
        tone: Desired tone
        length: Desired length
        keywords: SEO keywords
        content_type: Type of content
        context: Optional context information
        existing_content: Optional existing content to use as a base
        
    Returns:
        Generated content
    """
    print(f"Generating {content_type} about '{topic}' with {tone} tone")
    
    structure_guidance = get_content_structure(content_type)
    
    # Extract context if available
    seo_guidance = ""
    client_guidance = ""
    style_guidance = ""
    reference_docs = ""
    
    if context:
        # Add SEO recommendations
        if context.get("seo_analysis") and context["seo_analysis"].get("recommendations"):
            recs = context["seo_analysis"]["recommendations"]
            seo_guidance = "\n\nSEO Recommendations:\n" + "\n".join([f"- {rec}" for rec in recs])
            
            # Add word count if available
            if context["seo_analysis"].get("avg_word_count"):
                word_count = int(context["seo_analysis"]["avg_word_count"])
                seo_guidance += f"\n- Target word count based on competitors: {word_count} words"
        
        # Add client context
        if context.get("client_context"):
            client = context["client_context"]
            client_guidance = "\n\nClient Preferences:\n"
            
            if client.get("industry_terms") and isinstance(client["industry_terms"], list):
                terms = client["industry_terms"]
                if terms:
                    client_guidance += f"- Industry terms to include: {', '.join(terms)}\n"
            
            if client.get("tone") and client["tone"] != "unknown":
                client_guidance += f"- Preferred tone: {client['tone']}\n"
            
            if client.get("structure_preferences") and client["structure_preferences"] != "unknown":
                client_guidance += f"- Content structure: {client['structure_preferences']}\n"
            
            if client.get("target_audience") and isinstance(client["target_audience"], list):
                audience = client["target_audience"]
                if audience:
                    client_guidance += f"- Target audience: {', '.join(audience)}\n"
            
            if client.get("key_themes") and isinstance(client["key_themes"], list):
                themes = client["key_themes"]
                if themes:
                    client_guidance += f"- Key themes to emphasize: {', '.join(themes)}\n"
            
            if client.get("taboo_topics") and isinstance(client["taboo_topics"], list):
                taboos = client["taboo_topics"]
                if taboos:
                    client_guidance += f"- Topics/terms to avoid: {', '.join(taboos)}\n"
        
        # Add style guidance
        if context.get("specialist_style"):
            style = context["specialist_style"]
            style_guidance = "\n\nAdopt this writing style:\n"
            
            for key, value in style.items():
                if key != "overall_style" and value and value != "unknown":
                    style_guidance += f"- {key.replace('_', ' ').title()}: {value}\n"
            
            if style.get("overall_style") and style["overall_style"] != "unknown":
                style_guidance += f"\nOverall style: {style['overall_style']}\n"
        
        # Add reference documents
        if context.get("context_docs") and isinstance(context["context_docs"], list):
            docs = context["context_docs"]
            if docs:
                reference_docs = "\n\nReference from existing content:\n"
                for i, doc in enumerate(docs, 1):
                    content_snippet = doc.get('content', '')
                    if content_snippet:
                        # Limit to first 300 chars
                        snippet = content_snippet[:300] + ("..." if len(content_snippet) > 300 else "")
                        reference_docs += f"Reference {i}:\n{snippet}\n\n"
    
    # If we have existing content, create a modification prompt instead
    if existing_content:
        prompt = f"""
        You are a professional content writer and SEO expert. 
        
        You need to optimize the existing content below based on the topic '{topic}' 
        and keywords: {keywords}
        
        Content type: {content_type}
        Desired tone: {tone}
        Target length: {length}
        
        {seo_guidance}
        {client_guidance}
        {style_guidance}
        {reference_docs}
        
        Existing content to optimize:
        ```
        {existing_content}
        ```
        
        Make the following improvements:
        1. Ensure the content follows the structure for a {content_type}
        2. Optimize for the keywords naturally without keyword stuffing
        3. Adjust the tone to match the requested {tone} tone
        4. Apply all SEO recommendations and client preferences listed above
        5. Keep the overall message but improve clarity, flow, and SEO value
        
        Return the optimized content with appropriate markdown formatting.
        """
    else:
        # Build the enhanced prompt with all available context
        prompt = f"""
        You are a professional content writer specializing in {content_type}s.
        
        Create a {length} {content_type} about {topic} with a {tone} tone.
        Include these keywords naturally throughout the content: {keywords}
        
        {structure_guidance}
        {seo_guidance}
        {client_guidance}
        {style_guidance}
        {reference_docs}
        
        Create high-quality, original content that provides real value to the reader.
        Ensure all headings and formatting use proper markdown syntax.
        Naturally incorporate the keywords without keyword stuffing.
        
        Return only the content, formatted in markdown.
        """
    
    # Use the LLM to generate content
    try:
        model = "gpt-4o" if content_type in ["journal", "success_story"] or length.lower().startswith(("2000", "3000")) else "gpt-3.5-turbo"
        llm = initialize_llm(model_name=model, temperature=0.7)
        response = llm.invoke(prompt)
        
        # Clean up any extra quotes or markdown delimiters in the response
        content = response.content.strip()
        
        # Remove any markdown code block markers if they exist
        if content.startswith("```") and content.endswith("```"):
            content = content[content.find("\n")+1:content.rfind("```")].strip()
        elif content.startswith("```markdown") and content.endswith("```"):
            content = content[content.find("\n")+1:content.rfind("```")].strip()
        
        print(f"Generated {content_type} with {len(content.split())} words")
        return content
    
    except Exception as e:
        print(f"Error generating content: {e}")
        return f"Error generating content: {str(e)}"