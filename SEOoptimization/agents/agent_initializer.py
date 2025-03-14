from langchain.agents import initialize_agent, AgentType
from langchain_openai import ChatOpenAI

def initialize_agent_with_tools(tools):
    """Initialize the agent with the given tools."""
    llm = ChatOpenAI(model_name="gpt-3.5-turbo", temperature=0.7)
    return initialize_agent(
        tools=tools,
        llm=llm,
        agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
        verbose=True
    )