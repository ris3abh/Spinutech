from langchain.prompts import PromptTemplate

def optimize_for_seo(text):
    """Optimize the given text for SEO."""
    template = PromptTemplate.from_template("Optimize this text for SEO: {text}")
    from models.openai import initialize_llm  # Import here to avoid circular dependency
    
    llm = initialize_llm()
    response = llm.invoke(template.format_prompt(text=text))
    return response.content