from langchain.agents import initialize_agent, AgentType
from langchain_openai import ChatOpenAI
import warnings

def initialize_agent_with_tools(tools):
    """Initialize the agent with the given tools."""
    # Temporarily suppress the deprecation warnings
    warnings.filterwarnings("ignore", category=DeprecationWarning)
    
    llm = ChatOpenAI(model_name="gpt-3.5-turbo", temperature=0.7)
    
    # Create the agent with error handling for parsing
    agent = initialize_agent(
        tools=tools,
        llm=llm,
        agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
        verbose=True,
        handle_parsing_errors=True  # Add this to handle parsing errors
    )
    
    return agent