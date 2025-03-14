from langchain_openai import ChatOpenAI

def initialize_llm(model_name="gpt-3.5-turbo", temperature=0.7):
    """Initialize the OpenAI language model"""
    return ChatOpenAI(model_name=model_name, temperature=temperature)