"""
Enhanced workflow graph for content generation with style adaptation.
This module provides a flexible workflow that integrates client preferences,
specialist writing style, and multiple content types.
"""

import sys
from datetime import datetime
from typing import Literal, Dict, Any, List, Optional

from langchain.graphs import StateGraph, END
from langchain_core.messages import HumanMessage, AIMessage

from SEOoptimization.agents.enhanced_state import EnhancedAgentState
from SEOoptimization.utils.enhanced_knowledge_base import EnhancedKnowledgeBase
from SEOoptimization.tools.web_search_enhanced import analyze_keyword_direct
from SEOoptimization.tools.content_generator import generate_content_direct
from SEOoptimization.tools.style_adapter import adapt_style_direct
from SEOoptimization.tools.content_validator import validate_content_direct

sys.dont_write_bytecode = True  # Prevent __pycache__ creation

# Define node functions for the graph
def analyze_content_landscape_node(state: EnhancedAgentState) -> EnhancedAgentState:
    """Analyze the SEO landscape and client/specialist context."""
    topic = state["topic"]
    keywords = state["keywords"]
    content_type = state["content_type"]
    
    try:
        # Get client and specialist IDs
        client_id = state.get("client_id")
        specialist_id = state.get("specialist_id")
        
        # 1. Analyze the SEO landscape
        seo_analysis = analyze_keyword_direct(topic=topic, keywords=keywords)
        
        # 2. Initialize knowledge base
        kb = EnhancedKnowledgeBase()
        
        # 3. Get client-specific context if available
        client_context = {}
        if client_id:
            client_context = kb.analyze_client_content(client_id)
        
        # 4. Get specialist writing style if available
        specialist_style = {}
        if specialist_id:
            specialist_style = kb.analyze_writing_style(specialist_id)
        
        # Create new state with combined analysis
        new_state = state.copy()
        new_state["seo_analysis"] = seo_analysis
        new_state["client_context"] = client_context
        new_state["specialist_style"] = specialist_style
        
        # Get relevant content from knowledge base
        context_docs = []
        
        if client_id or specialist_id:
            filter_criteria = {}
            if client_id:
                filter_criteria["client_id"] = client_id
            if specialist_id:
                filter_criteria["owner_id"] = specialist_id
            
            context_docs = kb.search(
                query=f"{topic} {keywords}",
                filter_criteria=filter_criteria,
                top_k=5
            )
            
        new_state["context_docs"] = context_docs
        
        # Add analysis messages
        new_state["messages"] = state["messages"] + [
            AIMessage(content=f"✅ Completed content landscape analysis for '{topic}' ({content_type})")
        ]
        
        # Add recommendations to messages
        if seo_analysis and "recommendations" in seo_analysis and seo_analysis["recommendations"]:
            recommendations = "\n".join([f"- {rec}" for rec in seo_analysis["recommendations"]])
            new_state["messages"].append(
                AIMessage(content=f"SEO Recommendations:\n{recommendations}")
            )
        
        if client_context:
            # Extract main points from client context for message
            client_insights = "Client context insights:\n"
            
            if client_context.get("tone") and client_context["tone"] != "unknown":
                client_insights += f"- Preferred tone: {client_context['tone']}\n"
                
            if client_context.get("target_audience") and isinstance(client_context["target_audience"], list):
                audience = client_context["target_audience"]
                if audience:
                    client_insights += f"- Target audience: {', '.join(audience[:3])}"
                    if len(audience) > 3:
                        client_insights += " and others"
                    client_insights += "\n"
            
            if client_context.get("industry_terms") and isinstance(client_context["industry_terms"], list):
                terms = client_context["industry_terms"]
                if terms:
                    client_insights += f"- Key industry terms: {', '.join(terms[:3])}"
                    if len(terms) > 3:
                        client_insights += " and others"
                    client_insights += "\n"
            
            new_state["messages"].append(
                AIMessage(content=client_insights)
            )
        
        if specialist_style:
            new_state["messages"].append(
                AIMessage(content=f"Specialist writing style analyzed and will be applied.")
            )
        
        if context_docs:
            new_state["messages"].append(
                AIMessage(content=f"Found {len(context_docs)} relevant reference documents to inform content creation.")
            )
        
        return new_state
    
    except Exception as e:
        # Handle errors
        error_msg = f"Error analyzing content landscape: {str(e)}"
        new_state = state.copy()
        new_state["errors"] = state.get("errors", []) + [error_msg]
        new_state["messages"] = state["messages"] + [
            AIMessage(content=f"❌ Failed to analyze content landscape: {str(e)}")
        ]
        return new_state

def generate_content_node(state: EnhancedAgentState) -> EnhancedAgentState:
    """Generate the initial content draft with all available context."""
    topic = state["topic"]
    tone = state["tone"]
    length = state["length"]
    keywords = state["keywords"]
    content_type = state["content_type"]
    
    try:
        # Prepare context from multiple sources
        context = {
            "seo_analysis": state.get("seo_analysis", {}),
            "client_context": state.get("client_context", {}),
            "specialist_style": state.get("specialist_style", {}),
            "context_docs": state.get("context_docs", [])
        }
        
        # Generate content
        content_draft = generate_content_direct(
            topic=topic,
            tone=tone,
            length=length,
            keywords=keywords,
            content_type=content_type,
            context=context
        )
        
        # Create new state with the generated content
        new_state = state.copy()
        new_state["content_draft"] = content_draft
        new_state["messages"] = state["messages"] + [
            AIMessage(content=f"✅ Generated initial {content_type} draft for '{topic}' ({len(content_draft.split())} words)")
        ]
        return new_state
    
    except Exception as e:
        # Handle errors
        error_msg = f"Error generating content: {str(e)}"
        new_state = state.copy()
        new_state["errors"] = state.get("errors", []) + [error_msg]
        new_state["messages"] = state["messages"] + [
            AIMessage(content=f"❌ Failed to generate content: {str(e)}")
        ]
        return new_state

def adapt_style_node(state: EnhancedAgentState) -> EnhancedAgentState:
    """Adapt content style based on specialist and client patterns."""
    # Check if we have a content draft
    if not state.get("content_draft"):
        new_state = state.copy()
        error_msg = "Cannot adapt style: No content draft available"
        new_state["errors"] = state.get("errors", []) + [error_msg]
        new_state["messages"] = state["messages"] + [
            AIMessage(content=f"❌ {error_msg}")
        ]
        return new_state
    
    try:
        content_draft = state["content_draft"]
        specialist_style = state.get("specialist_style", {})
        client_context = state.get("client_context", {})
        
        # Skip adaptation if no style or context is available
        if not specialist_style and not client_context:
            new_state = state.copy()
            new_state["adapted_content"] = content_draft  # Use draft as-is
            new_state["messages"] = state["messages"] + [
                AIMessage(content="ℹ️ No specialist style or client context available for adaptation.")
            ]
            return new_state
        
        # Adapt content style
        adapted_content = adapt_style_direct(
            content=content_draft,
            specialist_style=specialist_style,
            client_context=client_context
        )
        
        # Create new state with the adapted content
        new_state = state.copy()
        new_state["adapted_content"] = adapted_content
        new_state["messages"] = state["messages"] + [
            AIMessage(content=f"✅ Adapted content style to match specialist and client preferences")
        ]
        return new_state
    
    except Exception as e:
        # Handle errors
        error_msg = f"Error adapting style: {str(e)}"
        new_state = state.copy()
        new_state["errors"] = state.get("errors", []) + [error_msg]
        # Still use the draft content if adaptation fails
        new_state["adapted_content"] = state["content_draft"]
        new_state["messages"] = state["messages"] + [
            AIMessage(content=f"⚠️ Style adaptation encountered an issue: {str(e)}. Proceeding with original draft.")
        ]
        return new_state

def optimize_content_node(state: EnhancedAgentState) -> EnhancedAgentState:
    """Optimize the content for SEO using all available insights."""
    # Check if we have adapted content or fall back to draft
    content_to_optimize = state.get("adapted_content") or state.get("content_draft")
    if not content_to_optimize:
        new_state = state.copy()
        error_msg = "Cannot optimize: No content available"
        new_state["errors"] = state.get("errors", []) + [error_msg]
        new_state["messages"] = state["messages"] + [
            AIMessage(content=f"❌ {error_msg}")
        ]
        return new_state
    
    try:
        # Get SEO analysis
        seo_analysis = state.get("seo_analysis", {})
        content_type = state["content_type"]
        topic = state["topic"]
        keywords = state["keywords"]
        
        # Use the content generator again but with existing content to optimize
        optimized_content = generate_content_direct(
            topic=topic,
            tone=state["tone"],
            length=state["length"],
            keywords=keywords,
            content_type=content_type,
            context={"seo_analysis": seo_analysis},
            existing_content=content_to_optimize  # Pass the content to optimize
        )
        
        # Create new state with the optimized content
        new_state = state.copy()
        new_state["final_content"] = optimized_content
        new_state["messages"] = state["messages"] + [
            AIMessage(content=f"✅ {content_type.capitalize()} has been optimized for SEO")
        ]
        return new_state
    
    except Exception as e:
        # Handle errors
        error_msg = f"Error optimizing content: {str(e)}"
        new_state = state.copy()
        new_state["errors"] = state.get("errors", []) + [error_msg]
        # Still use the adapted/draft content if optimization fails
        new_state["final_content"] = content_to_optimize
        new_state["messages"] = state["messages"] + [
            AIMessage(content=f"⚠️ SEO optimization encountered an issue: {str(e)}. Using previous content version.")
        ]
        return new_state

def validate_content_node(state: EnhancedAgentState) -> EnhancedAgentState:
    """Generate validation report for the final content."""
    # Check if we have final content or fall back to adapted/draft
    content_to_validate = state.get("final_content") or state.get("adapted_content") or state.get("content_draft")
    if not content_to_validate:
        new_state = state.copy()
        error_msg = "Cannot validate: No content available"
        new_state["errors"] = state.get("errors", []) + [error_msg]
        new_state["messages"] = state["messages"] + [
            AIMessage(content=f"❌ {error_msg}")
        ]
        return new_state
    
    try:
        # Get necessary inputs
        topic = state["topic"]
        keywords = state["keywords"]
        seo_analysis = state.get("seo_analysis", {})
        content_type = state["content_type"]
        
        # Generate validation report
        validation_report = validate_content_direct(
            content=content_to_validate,
            topic=topic,
            keywords=keywords,
            seo_analysis=seo_analysis,
            content_type=content_type
        )
        
        # Create new state with the validation report
        new_state = state.copy()
        new_state["validation_report"] = validation_report
        
        # Add a message with key validation insights
        validation_message = f"✅ Content validation complete:\n"
        
        if "validation" in validation_report:
            v = validation_report["validation"]
            validation_message += f"- SEO Score: {v.get('seo_score', 'N/A')}/100\n"
            validation_message += f"- Content Quality Score: {v.get('content_quality_score', 'N/A')}/100\n"
            
            if "recommendations" in v and v["recommendations"]:
                validation_message += "\nImprovement recommendations:\n"
                for i, rec in enumerate(v["recommendations"][:3], 1):
                    validation_message += f"{i}. {rec}\n"
        
        if "metrics" in validation_report:
            m = validation_report["metrics"]
            validation_message += f"\nWord count: {m.get('word_count', 'N/A')} words\n"
            
            # Add keyword coverage stats
            if "keyword_stats" in m:
                keyword_stats = m["keyword_stats"]
                
                # Calculate how many keywords are in title/headings
                keywords_in_title = sum(1 for k, v in keyword_stats.items() if v.get("in_title", False))
                keywords_in_headings = sum(1 for k, v in keyword_stats.items() if v.get("in_headings", False))
                total_keywords = len(keyword_stats)
                
                if total_keywords > 0:
                    validation_message += f"- Keywords in title: {keywords_in_title}/{total_keywords}\n"
                    validation_message += f"- Keywords in headings: {keywords_in_headings}/{total_keywords}\n"
        
        new_state["messages"].append(
            AIMessage(content=validation_message)
        )
        
        return new_state
    
    except Exception as e:
        # Handle errors
        error_msg = f"Error validating content: {str(e)}"
        new_state = state.copy()
        new_state["errors"] = state.get("errors", []) + [error_msg]
        new_state["messages"] = state["messages"] + [
            AIMessage(content=f"⚠️ Content validation encountered an issue: {str(e)}. Skipping validation step.")
        ]
        return new_state

# Define routing logic
def should_generate_or_end(state: EnhancedAgentState) -> Literal["generate", "end"]:
    """Decide whether to generate the content or end the workflow."""
    if not state.get("errors"):
        return "generate"
    return "end"

def should_adapt_or_end(state: EnhancedAgentState) -> Literal["adapt", "end"]:
    """Decide whether to adapt the content style or end the workflow."""
    if state.get("content_draft") and not state.get("errors"):
        return "adapt"
    return "end"

def should_optimize_or_end(state: EnhancedAgentState) -> Literal["optimize", "end"]:
    """Decide whether to optimize the content or end the workflow."""
    if (state.get("adapted_content") or state.get("content_draft")) and not state.get("errors"):
        return "optimize"
    return "end"

def should_validate_or_end(state: EnhancedAgentState) -> Literal["validate", "end"]:
    """Decide whether to validate the content or end the workflow."""
    if (state.get("final_content") or state.get("adapted_content") or state.get("content_draft")) and not state.get("errors"):
        return "validate"
    return "end"

def build_enhanced_workflow() -> StateGraph:
    """Build and return the enhanced content generation workflow graph."""
    # Create the workflow graph
    workflow = StateGraph(EnhancedAgentState)
    
    # Add nodes
    workflow.add_node("analyze_content_landscape", analyze_content_landscape_node)
    workflow.add_node("generate_content", generate_content_node)
    workflow.add_node("adapt_style", adapt_style_node)
    workflow.add_node("optimize_content", optimize_content_node)
    workflow.add_node("validate_content", validate_content_node)
    
    # Add edges with conditional routing
    workflow.add_conditional_edges(
        "analyze_content_landscape",
        should_generate_or_end,
        {
            "generate": "generate_content",
            "end": END
        }
    )
    
    workflow.add_conditional_edges(
        "generate_content",
        should_adapt_or_end,
        {
            "adapt": "adapt_style",
            "end": END
        }
    )
    
    workflow.add_conditional_edges(
        "adapt_style",
        should_optimize_or_end,
        {
            "optimize": "optimize_content",
            "end": END
        }
    )
    
    workflow.add_conditional_edges(
        "optimize_content",
        should_validate_or_end,
        {
            "validate": "validate_content",
            "end": END
        }
    )
    
    workflow.add_edge("validate_content", END)
    
    # Set the entry point
    workflow.set_entry_point("analyze_content_landscape")
    
    # Compile the workflow
    return workflow.compile()

def create_enhanced_initial_state(
    topic: str, 
    tone: str, 
    length: str, 
    keywords: str,
    content_type: str = "article",
    client_id: Optional[str] = None,
    specialist_id: Optional[str] = None
) -> EnhancedAgentState:
    """Create the initial state for the enhanced workflow."""
    # Get current timestamp
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    
    return {
        "topic": topic,
        "tone": tone,
        "length": length,
        "keywords": keywords,
        "content_type": content_type,
        "client_id": client_id,
        "specialist_id": specialist_id,
        "messages": [
            HumanMessage(content=f"Generate a {content_type} about '{topic}' with {tone} tone, {length} long, using keywords: {keywords}")
        ],
        "seo_analysis": None,
        "client_context": None,
        "specialist_style": None,
        "context_docs": None,
        "content_draft": None,
        "adapted_content": None,
        "final_content": None,
        "validation_report": None,
        "errors": [],
        "timestamp": timestamp
    }

def run_enhanced_workflow(
    topic: str, 
    tone: str, 
    length: str, 
    keywords: str,
    content_type: str = "article",
    client_id: Optional[str] = None,
    specialist_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    Run the enhanced content generation workflow and return the result.
    
    Args:
        topic: Content topic
        tone: Desired tone
        length: Desired length
        keywords: SEO keywords
        content_type: Type of content (article, landing_page, journal, success_story)
        client_id: Optional client ID for personalization
        specialist_id: Optional specialist ID for style adaptation
        
    Returns:
        Dictionary with workflow results
    """
    print(f"\n{'='*80}")
    print(f"Starting Enhanced Content Generation for: {topic} ({content_type})")
    if client_id:
        print(f"Client ID: {client_id}")
    if specialist_id:
        print(f"Specialist ID: {specialist_id}")
    print(f"{'='*80}\n")
    
    # Build the workflow
    workflow = build_enhanced_workflow()
    
    # Create initial state
    initial_state = create_enhanced_initial_state(
        topic=topic,
        tone=tone,
        length=length,
        keywords=keywords,
        content_type=content_type,
        client_id=client_id,
        specialist_id=specialist_id
    )
    
    # Run the workflow
    result = workflow.invoke(initial_state)
    
    print(f"\n{'='*80}")
    print(f"Workflow Complete for: {topic}")
    print(f"{'='*80}\n")
    
    return result