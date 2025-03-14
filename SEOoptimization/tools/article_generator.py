from langchain_core.prompts import PromptTemplate
from langchain_core.tools import tool

from SEOoptimization.models.openai import initialize_llm
from SEOoptimization.prompts.article_prompt import article_prompt

def parse_input(input_text):
    """Parse input text to extract topic, tone, length, and keywords."""
    # Handle case where input might have extra formatting
    if input_text.startswith("'") and input_text.endswith("'"):
        input_text = input_text[1:-1]  # Remove surrounding quotes
    
    parts = input_text.split(',', 3)  # Split into max 4 parts
    
    if len(parts) < 4:
        raise ValueError("Input must contain topic, tone, length, and keywords separated by commas. "
                         "Format: 'topic, tone, length, keywords: keyword1, keyword2'")
    
    topic = parts[0].strip()
    tone = parts[1].strip()
    length = parts[2].strip()
    
    # Extract keywords from the last part
    keywords_part = parts[3].strip()
    if "keywords:" not in keywords_part.lower():
        raise ValueError("Keywords section must be formatted as 'keywords: keyword1, keyword2, etc'")
    
    keywords = keywords_part.split('keywords:', 1)[1].strip()
    
    return topic, tone, length, keywords

@tool
def generate_article(input_text: str) -> str:
    """Generate a blog post based on the input text.
    
    The input_text must contain topic, tone, length, and keywords information in the format:
    'topic, tone, length, keywords: keyword1, keyword2, etc'
    """
    try:
        # Try to parse the input
        topic, tone, length, keywords = parse_input(input_text)
        
        llm = initialize_llm()
        
        response = llm.invoke(article_prompt.format_prompt(
            topic=topic, 
            tone=tone, 
            length=length, 
            keywords=keywords
        ))
        return response.content
    except Exception as e:
        # For debugging purposes
        error_message = f"Error in generate_article: {str(e)}\nInput text: {input_text}"
        print(error_message)
        # Re-raise the error for proper handling
        raise

# Function version for direct use in the graph
def generate_article_direct(topic: str, tone: str, length: str, keywords: str) -> str:
    """Generate a blog post with the given parameters.
    This function is meant to be called directly from the graph, not as a tool.
    """
    llm = initialize_llm()
    
    response = llm.invoke(article_prompt.format_prompt(
        topic=topic, 
        tone=tone, 
        length=length, 
        keywords=keywords
    ))
    return response.content