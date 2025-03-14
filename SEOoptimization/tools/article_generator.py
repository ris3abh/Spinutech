from langchain.prompts import PromptTemplate
from langchain_community.utilities import WikipediaAPIWrapper

# Initialize Wikipedia API wrapper
wikipedia = WikipediaAPIWrapper()

# Article generation prompt template
article_prompt = PromptTemplate(
    input_variables=["topic", "tone", "length", "keywords"],
    template="""
    You are a professional blogger and technical writer. Write a {length} article about {topic} 
    with a {tone} tone. Include these keywords: {keywords}. Structure the article with:
    - Catchy title
    - Introduction
    - 3-5 main sections
    - Conclusion
    - SEO-optimized meta description
    """
)

def parse_input(input_text):
    """Parse input text to extract topic, tone, length, and keywords."""
    # First, handle the case where the input might be formatted with quotes and parentheses
    # as seen in the error output
    if input_text.startswith("'") and input_text.endswith("'"):
        input_text = input_text[1:-1]  # Remove surrounding quotes
    
    if "keywords:" in input_text.lower():
        # Split by "keywords:" to separate the first part from keywords
        parts = input_text.lower().split("keywords:", 1)
        first_part = parts[0].strip()
        keywords = parts[1].strip()
        
        # Split the first part by commas to get topic, tone, and length
        first_parts = first_part.split(",")
        if len(first_parts) >= 3:
            topic = first_parts[0].strip()
            tone = first_parts[1].strip()
            length = first_parts[2].strip()
            return topic, tone, length, keywords
    
    # If we get here, the format wasn't as expected, try a more forgiving approach
    parts = input_text.split(",")
    if len(parts) >= 4:
        topic = parts[0].strip()
        tone = parts[1].strip()
        length = parts[2].strip()
        keywords = ",".join(parts[3:]).strip()
        
        # Check if keywords has the "keywords:" prefix and remove if present
        if "keywords:" in keywords.lower():
            keywords = keywords.lower().split("keywords:", 1)[1].strip()
        
        return topic, tone, length, keywords
    
    # If all else fails, raise an error
    raise ValueError(f"Could not parse input: {input_text}. Expected format: 'topic, tone, length, keywords: keyword1, keyword2'")

def generate_article(input_text):
    """Generate a blog post based on the input text."""
    from models.openai import initialize_llm  # Import here to avoid circular dependency
    
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