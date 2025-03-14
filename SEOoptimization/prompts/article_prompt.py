from langchain.prompts import PromptTemplate

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