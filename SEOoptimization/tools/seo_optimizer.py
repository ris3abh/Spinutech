from langchain_core.prompts import PromptTemplate
from langchain_core.tools import tool
from SEOoptimization.models.openai import initialize_llm

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

@tool
def optimize_for_seo(text: str) -> str:
    """Optimize the given text for SEO."""
    llm = initialize_llm()
    response = llm.invoke(seo_prompt.format_prompt(text=text))
    return response.content

# Function version for direct use in the graph
def optimize_for_seo_direct(text: str) -> str:
    """Optimize the given text for SEO.
    This function is meant to be called directly from the graph, not as a tool.
    """
    llm = initialize_llm()
    response = llm.invoke(seo_prompt.format_prompt(text=text))
    return response.content