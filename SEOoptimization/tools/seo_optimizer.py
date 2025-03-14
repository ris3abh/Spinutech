from langchain.prompts import PromptTemplate

seo_prompt = PromptTemplate(
    input_variables=["text"],
    template="""
    You are an SEO expert. Optimize the following text for search engines without
    changing the core content or voice. 
    
    Make these improvements:
    1. Ensure headlines include target keywords
    2. Add appropriate meta tags
    3. Optimize keyword density (2-3%)
    4. Improve readability with subheadings and bullet points where relevant
    5. Add appropriate internal and external link placeholders
    6. Ensure proper header hierarchy (H1, H2, H3)
    
    Original text:
    {text}
    
    SEO Optimized Version:
    """
)

def optimize_for_seo(text):
    """Optimize the given text for SEO."""
    from models.openai import initialize_llm  # Import here to avoid circular dependency
    
    llm = initialize_llm()
    response = llm.invoke(seo_prompt.format_prompt(text=text))
    return response.content