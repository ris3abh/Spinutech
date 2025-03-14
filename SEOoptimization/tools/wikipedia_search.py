from langchain_community.utilities import WikipediaAPIWrapper
from langchain_core.tools import tool

wikipedia = WikipediaAPIWrapper()

@tool
def wikipedia_search(query: str) -> str:
    """Search Wikipedia for the given query."""
    return wikipedia.run(query)