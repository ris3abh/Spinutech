import sys
sys.dont_write_bytecode = True

import os
import argparse
from config.env import load_environment
from tools.article_generator import generate_article
from tools.wikipedia_search import wikipedia_search
from tools.seo_optimizer import optimize_for_seo
from langchain.agents import Tool
from agents.agent_initializer import initialize_agent_with_tools

# Load environment variables
load_environment()

# Define custom tools
tools = [
    Tool(
        name="ArticleGenerator",
        func=generate_article,
        description="Useful for generating blog posts and articles. Input format: 'topic, tone, length, keywords: keyword1, keyword2'. Example: 'Compact Tractors, professional, 1200 words, keywords: farming equipment, agricultural machinery'"
    ),
    Tool(
        name="WikipediaSearch",
        func=wikipedia_search,
        description="Useful for finding information about a topic. Input should be a search query."
    )
]

# Initialize agent
agent = initialize_agent_with_tools(tools)

# Example usage
if __name__ == "__main__":
    # Set up argument parsing
    parser = argparse.ArgumentParser(description='Generate articles with customizable parameters.')
    parser.add_argument('--topic', type=str, required=True, help='Topic of the article')
    parser.add_argument('--tone', type=str, default="professional", help='Tone of the article (default: professional)')
    parser.add_argument('--length', type=str, default="1000 words", help='Length of the article (default: 1000 words)')
    parser.add_argument('--keywords', type=str, default="LangChain, agents, AI, automation", help='Keywords to include in the article (comma-separated)')
    parser.add_argument('--debug', action='store_true', help='Enable debug mode for more detailed error messages')
    
    args = parser.parse_args()

    try:
        # Format the input for the agent
        agent_input = f"{args.topic}, {args.tone}, {args.length}, keywords: {args.keywords}"
        
        if args.debug:
            print(f"Debug: Agent input: {agent_input}")
        
        # Use invoke() instead of run() to address the deprecation warning
        response = agent.invoke({"input": agent_input})
        
        # Extract the output from the response
        article_content = response.get("output", "")
        
        if not article_content and args.debug:
            print("Debug: Empty article content. Full response:")
            print(response)
        
        # Optionally run SEO optimization
        optimized = optimize_for_seo(article_content)
        print("\n--- SEO Optimized Article ---\n")
        print(optimized)
        
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        # Print more detailed error information if in debug mode
        if args.debug:
            import traceback
            traceback.print_exc()