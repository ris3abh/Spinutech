import sys
from typing import Literal, Dict, Any

from langgraph.graph import StateGraph, END
from langchain_core.messages import HumanMessage, AIMessage

from SEOoptimization.agents.state import AgentState
from SEOoptimization.tools.article_generator import generate_article_direct
from SEOoptimization.tools.seo_optimizer import optimize_for_seo_direct

sys.dont_write_bytecode = True  # Prevent __pycache__ creation

# Define node functions for the graph
def generate_article_node(state: AgentState) -> AgentState:
    """Generate the initial article draft."""
    topic = state["topic"]
    tone = state["tone"]
    length = state["length"]
    keywords = state["keywords"]
    
    try:
        # Generate article
        article = generate_article_direct(
            topic=topic,
            tone=tone,
            length=length,
            keywords=keywords
        )
        
        # Create new state with the generated article
        new_state = state.copy()
        new_state["article_draft"] = article
        new_state["messages"] = state["messages"] + [
            AIMessage(content=f"✅ Generated article draft about '{topic}' with {tone} tone.")
        ]
        return new_state
    
    except Exception as e:
        # Handle errors
        error_msg = f"Error generating article: {str(e)}"
        new_state = state.copy()
        new_state["errors"] = state.get("errors", []) + [error_msg]
        new_state["messages"] = state["messages"] + [
            AIMessage(content=f"❌ Failed to generate article: {str(e)}")
        ]
        return new_state

def optimize_article_node(state: AgentState) -> AgentState:
    """Optimize the article for SEO."""
    # Check if we have an article draft
    if not state.get("article_draft"):
        new_state = state.copy()
        error_msg = "Cannot optimize: No article draft available"
        new_state["errors"] = state.get("errors", []) + [error_msg]
        new_state["messages"] = state["messages"] + [
            AIMessage(content=f"❌ {error_msg}")
        ]
        return new_state
    
    try:
        # Optimize the article
        optimized = optimize_for_seo_direct(state["article_draft"])
        
        # Create new state with the optimized article
        new_state = state.copy()
        new_state["final_article"] = optimized
        new_state["messages"] = state["messages"] + [
            AIMessage(content="✅ Article has been optimized for SEO.")
        ]
        return new_state
        
    except Exception as e:
        # Handle errors
        error_msg = f"Error optimizing article: {str(e)}"
        new_state = state.copy()
        new_state["errors"] = state.get("errors", []) + [error_msg]
        new_state["messages"] = state["messages"] + [
            AIMessage(content=f"❌ Failed to optimize article: {str(e)}")
        ]
        return new_state

# Define routing logic
def should_optimize_or_end(state: AgentState) -> Literal["optimize", "end"]:
    """Decide whether to optimize the article or end the workflow."""
    if state.get("article_draft") and not state.get("errors"):
        return "optimize"
    return "end"

def build_workflow() -> StateGraph:
    """Build and return the SEO optimization workflow graph."""
    # Create the workflow graph
    workflow = StateGraph(AgentState)
    
    # Add nodes
    workflow.add_node("generate_article", generate_article_node)
    workflow.add_node("optimize_article", optimize_article_node)
    
    # Add edges
    workflow.add_conditional_edges(
        "generate_article",
        should_optimize_or_end,
        {
            "optimize": "optimize_article",
            "end": END
        }
    )
    workflow.add_edge("optimize_article", END)
    
    # Set the entry point
    workflow.set_entry_point("generate_article")
    
    # Compile the workflow
    return workflow.compile()

def create_initial_state(topic: str, tone: str, length: str, keywords: str) -> AgentState:
    """Create the initial state for the workflow."""
    return {
        "topic": topic,
        "tone": tone,
        "length": length,
        "keywords": keywords,
        "messages": [
            HumanMessage(content=f"Generate an article about '{topic}' with {tone} tone, {length} long, using keywords: {keywords}")
        ],
        "article_draft": None,
        "final_article": None,
        "errors": []
    }

def run_seo_workflow(topic: str, tone: str, length: str, keywords: str) -> Dict[str, Any]:
    """Run the SEO optimization workflow and return the result."""
    # Build the workflow
    workflow = build_workflow()
    
    # Create initial state
    initial_state = create_initial_state(topic, tone, length, keywords)
    
    # Run the workflow
    result = workflow.invoke(initial_state)
    
    return result