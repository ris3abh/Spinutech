"""
Content validation tools for SEO and quality assessment.
This module provides functions to validate content against SEO best practices
and generate detailed reports.
"""

from typing import Dict, Any, List
import json
import re
from SEOoptimization.models.openai import initialize_llm

def validate_content_direct(
    content: str,
    topic: str,
    keywords: str,
    seo_analysis: Dict[str, Any] = None,
    content_type: str = "article"
) -> Dict[str, Any]:
    """
    Validate content against SEO best practices and generate report.
    
    Args:
        content: Final content to validate
        topic: Original topic
        keywords: Target keywords
        seo_analysis: SEO analysis results
        content_type: Type of content
        
    Returns:
        Dictionary with validation metrics and recommendations
    """
    print(f"Validating {content_type} about '{topic}'")
    
    # Calculate basic metrics
    word_count = len(content.split())
    
    # Convert keywords to list
    keywords_list = [k.strip() for k in keywords.split(',')]
    
    # Calculate keyword usage
    keyword_stats = {}
    for keyword in keywords_list:
        # Skip empty keywords
        if not keyword:
            continue
            
        # Count occurrences
        count = content.lower().count(keyword.lower())
        
        # Check if in title (first line)
        title = content.split('\n')[0] if '\n' in content else ""
        title = re.sub(r'^#\s+', '', title)  # Remove markdown heading
        in_title = keyword.lower() in title.lower()
        
        # Check if in headings (lines starting with #)
        in_headings = False
        headings = [line for line in content.split('\n') if line.strip().startswith('#')]
        for heading in headings:
            heading_text = re.sub(r'^#+\s+', '', heading)  # Remove markdown heading marks
            if keyword.lower() in heading_text.lower():
                in_headings = True
                break
        
        # Store stats
        keyword_stats[keyword] = {
            "count": count,
            "in_title": in_title,
            "in_headings": in_headings,
            "density": count / word_count * 100 if word_count else 0
        }
    
    # Count headings by level
    heading_counts = {}
    for i in range(1, 7):
        pattern = r'^#{' + str(i) + r'}\s+'
        heading_counts[f"h{i}"] = len(re.findall(pattern, content, re.MULTILINE))
    
    # Extract SEO meta description if present
    meta_description = ""
    meta_match = re.search(r'<!--\s*Meta:\s*(.*?)\s*-->', content, re.DOTALL)
    if meta_match:
        meta_description = meta_match.group(1).strip()
    
    # Get advanced validation from LLM
    validation_prompt = f"""
    You are an SEO expert and content quality analyst. Analyze this {content_type} for SEO effectiveness and content quality.
    
    Topic: {topic}
    Target Keywords: {keywords}
    Content Type: {content_type}
    Word Count: {word_count} words
    
    Content to analyze:
    ```
    {content}
    ```
    
    Provide a detailed validation report with these sections:
    
    1. SEO Score (0-100): Assign a score based on keyword usage, structure, and best practices
    2. Content Quality Score (0-100): Assess readability, clarity, value, and engagement 
    3. Keyword Usage: Evaluate how well keywords are incorporated
    4. Readability Assessment: Evaluate sentence structure, complexity, and flow
    5. Structure Evaluation: Assess the content organization and heading structure
    6. Specificity and Depth: Evaluate how well the content covers the topic
    7. Justification: Provide specific reasons for why certain content choices were made
    8. Improvement Recommendations: List 3-5 specific suggestions to improve the content
    
    Provide your report as a valid JSON object with the following structure:
    {{
        "seo_score": 85,
        "content_quality_score": 90,
        "keyword_usage": "Detailed evaluation...",
        "readability": "Detailed assessment...",
        "structure": "Structure evaluation...",
        "specificity": "Depth analysis...",
        "justifications": ["Reason 1...", "Reason 2...", "Reason 3..."],
        "recommendations": ["Suggestion 1...", "Suggestion 2...", "Suggestion 3..."]
    }}
    
    Return ONLY the JSON object, nothing else.
    """
    
    try:
        # Use a model suitable for analysis
        llm = initialize_llm(model_name="gpt-4o", temperature=0.2)
        response = llm.invoke(validation_prompt)
        
        # Parse JSON response
        try:
            validation_report = json.loads(response.content)
        except json.JSONDecodeError:
            # Try to extract JSON from the response if direct parsing fails
            import re
            json_match = re.search(r'({[\s\S]*})', response.content)
            if json_match:
                try:
                    validation_report = json.loads(json_match.group(1))
                except:
                    # If still fails, use fallback
                    validation_report = {
                        "seo_score": 0,
                        "content_quality_score": 0,
                        "keyword_usage": "Could not analyze",
                        "readability": "Could not analyze",
                        "structure": "Could not analyze",
                        "specificity": "Could not analyze",
                        "justifications": ["Could not generate justifications"],
                        "recommendations": ["Run validation again"]
                    }
            else:
                # No JSON found, use fallback
                validation_report = {
                    "seo_score": 0,
                    "content_quality_score": 0,
                    "keyword_usage": "Could not analyze",
                    "readability": "Could not analyze",
                    "structure": "Could not analyze",
                    "specificity": "Could not analyze",
                    "justifications": ["Could not generate justifications"],
                    "recommendations": ["Run validation again"]
                }
    except Exception as e:
        print(f"Error in content validation: {e}")
        validation_report = {
            "seo_score": 0,
            "content_quality_score": 0,
            "keyword_usage": f"Error: {str(e)}",
            "readability": "Could not analyze",
            "structure": "Could not analyze",
            "specificity": "Could not analyze",
            "justifications": ["Error occurred during validation"],
            "recommendations": ["Try again with a different validator"]
        }
    
    # Combine computed metrics with LLM analysis
    full_report = {
        "metrics": {
            "word_count": word_count,
            "keyword_stats": keyword_stats,
            "heading_counts": heading_counts,
            "meta_description_length": len(meta_description) if meta_description else 0,
            "meta_description_has_keywords": any(kw.lower() in meta_description.lower() for kw in keywords_list) if meta_description else False
        },
        "validation": validation_report
    }
    
    return full_report