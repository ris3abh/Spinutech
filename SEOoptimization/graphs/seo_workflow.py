# SEOoptimization/graphs/seo_workflow.py
import sys
from typing import Literal, Dict, Any

from langgraph.graph import StateGraph, END
from langchain_core.messages import HumanMessage, AIMessage

from SEOoptimization.agents.state import AgentState
from SEOoptimization.tools.article_generator import generate_article_direct
from SEOoptimization.tools.seo_optimizer import optimize_for_seo_direct
from SEOoptimization.tools.web_search_enhanced import analyze_keyword_direct

sys.dont_write_bytecode = True  # Prevent __pycache__ creation

# Define node functions for the graph
def analyze_seo_landscape_node(state: AgentState) -> AgentState:
    """Analyze the SEO landscape for the topic and keywords."""
    topic = state["topic"]
    keywords = state["keywords"]
    
    try:
        # Analyze the SEO landscape
        seo_analysis = analyze_keyword_direct(topic=topic, keywords=keywords)
        
        # Create new state with the SEO analysis
        new_state = state.copy()
        new_state["seo_analysis"] = seo_analysis
        new_state["messages"] = state["messages"] + [
            AIMessage(content=f"✅ Completed SEO analysis for '{topic}' with focus on keywords: {keywords}")
        ]
        
        # Add SEO recommendations to messages for clarity
        if seo_analysis.get("recommendations"):
            recommendations = "\n".join([f"- {rec}" for rec in seo_analysis["recommendations"]])
            new_state["messages"].append(
                AIMessage(content=f"SEO Recommendations:\n{recommendations}")
            )
        
        return new_state
    
    except Exception as e:
        # Handle errors
        error_msg = f"Error analyzing SEO landscape: {str(e)}"
        new_state = state.copy()
        new_state["errors"] = state.get("errors", []) + [error_msg]
        new_state["messages"] = state["messages"] + [
            AIMessage(content=f"❌ Failed to analyze SEO landscape: {str(e)}")
        ]
        return new_state

def generate_article_node(state: AgentState) -> AgentState:
    """Generate the initial article draft with SEO insights."""
    topic = state["topic"]
    tone = state["tone"]
    length = state["length"]
    keywords = state["keywords"]
    
    try:
        # Check if we have SEO analysis
        seo_guidance = ""
        if state.get("seo_analysis") and "recommendations" in state["seo_analysis"]:
            seo_recommendations = "\n".join([f"- {rec}" for rec in state["seo_analysis"]["recommendations"]])
            seo_guidance = f"\n\nFollow these SEO recommendations based on competitor analysis:\n{seo_recommendations}"
            
            # Add word count guidance if available
            if "avg_word_count" in state["seo_analysis"] and state["seo_analysis"]["avg_word_count"] > 0:
                target_word_count = int(state["seo_analysis"]["avg_word_count"])
                seo_guidance += f"\n\nTarget word count: {target_word_count} words (based on top-ranking competitors)"
        
        # Generate article with enhanced prompt
        enhanced_prompt = f"""
        You are a professional blogger and technical writer. Write a {length} article about {topic} 
        with a {tone} tone. Include these keywords: {keywords}.
        
        Structure the article with:
        - Catchy title that includes main keywords
        - Introduction that hooks the reader and includes primary keywords
        - 3-5 main sections with appropriate headings
        - Conclusion with a clear call to action
        - SEO-optimized meta description
        {seo_guidance}
        """
        
        # Use the LLM directly for more control
        from SEOoptimization.models.openai import initialize_llm
        llm = initialize_llm(model_name="gpt-4o", temperature=0.7)  # Use a more capable model
        
        response = llm.invoke(enhanced_prompt)
        article = response.content
        
        # Create new state with the generated article
        new_state = state.copy()
        new_state["article_draft"] = article
        new_state["messages"] = state["messages"] + [
            AIMessage(content=f"✅ Generated SEO-informed article draft about '{topic}' with {tone} tone.")
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
    """Optimize the article for SEO using competitor insights."""
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
        # Get SEO insights if available
        seo_insights = ""
        if state.get("seo_analysis"):
            seo_insights = "SEO insights from competitor analysis:\n"
            
            # Add keyword density information
            if "keyword_density" in state["seo_analysis"]:
                density = state["seo_analysis"]["keyword_density"]
                seo_insights += f"- Keyword density in titles: {density.get('title', 0)*100:.1f}%\n"
                seo_insights += f"- Keyword density in headings: {density.get('headings', 0)*100:.1f}%\n"
                seo_insights += f"- Keyword density in content: {density.get('content', 0):.2f}%\n"
            
            # Add link recommendations
            if "link_patterns" in state["seo_analysis"]:
                links = state["seo_analysis"]["link_patterns"]
                seo_insights += f"- Target internal links: {int(links.get('avg_internal', 0))}\n"
                seo_insights += f"- Target external links: {int(links.get('avg_external', 0))}\n"
        
        # Enhanced SEO prompt with competitor insights
        enhanced_seo_prompt = f"""
        You are an SEO expert. Optimize the following article for search engines while
        maintaining the original voice and quality of the content.
        
        Make these improvements:
        1. Ensure headlines include target keywords naturally
        2. Add appropriate meta tags and structured data recommendations
        3. Optimize keyword density to match competitor averages
        4. Improve readability with subheadings and bullet points where relevant
        5. Add appropriate internal and external link placeholders
        6. Ensure proper header hierarchy (H1, H2, H3)
        7. Optimize intro paragraph to grab attention and include primary keywords
        
        Keywords to focus on: {state["keywords"]}
        
        {seo_insights}
        
        Original article:
        {state["article_draft"]}
        
        SEO Optimized Version:
        """
        
        # Use the LLM directly for more control
        from SEOoptimization.models.openai import initialize_llm
        llm = initialize_llm(model_name="gpt-4o", temperature=0.3)  # Lower temperature for more focus
        
        response = llm.invoke(enhanced_seo_prompt)
        optimized = response.content
        
        # Create new state with the optimized article
        new_state = state.copy()
        new_state["final_article"] = optimized
        new_state["messages"] = state["messages"] + [
            AIMessage(content="✅ Article has been optimized for SEO using competitor insights.")
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
def should_generate_or_end(state: AgentState) -> Literal["generate", "end"]:
    """Decide whether to generate the article or end the workflow."""
    if not state.get("errors"):
        return "generate"
    return "end"

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
    workflow.add_node("analyze_seo_landscape", analyze_seo_landscape_node)
    workflow.add_node("generate_article", generate_article_node)
    workflow.add_node("optimize_article", optimize_article_node)
    
    # Add edges
    workflow.add_conditional_edges(
        "analyze_seo_landscape",
        should_generate_or_end,
        {
            "generate": "generate_article",
            "end": END
        }
    )
    
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
    workflow.set_entry_point("analyze_seo_landscape")
    
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
            HumanMessage(content=f"Generate an SEO-optimized article about '{topic}' with {tone} tone, {length} long, using keywords: {keywords}")
        ],
        "seo_analysis": None,
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