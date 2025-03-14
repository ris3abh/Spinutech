from langchain_community.utilities import WikipediaAPIWrapper

wikipedia = WikipediaAPIWrapper()

def wikipedia_search(query):
    """Search Wikipedia for the given query."""
    return wikipedia.run(query)