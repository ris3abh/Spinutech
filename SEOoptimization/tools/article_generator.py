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

def generate_article(topic, tone, length, keywords):
    """Generate a blog post on the given topic."""
    from models.openai import initialize_llm  # Import here to avoid circular dependency
    
    llm = initialize_llm()
    
    response = llm.invoke(article_prompt.format_prompt(
        topic=topic, 
        tone=tone, 
        length=length, 
        keywords=keywords
    ))
    return response.content