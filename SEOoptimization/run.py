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
        description="Useful for generating blog posts and articles. Input should be the topic you want to write about."
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
    
    args = parser.parse_args()

    try:
        # Generate article with parameters from command line
        response = agent.run(f"Generate a blog post about {args.topic} with a {args.tone} tone, approximately {args.length} long, including these keywords: {args.keywords}")
        # Optionally run SEO optimization
        optimized = optimize_for_seo(response)
        print("\n--- SEO Optimized Article ---\n")
        print(optimized)
        
    except Exception as e:
        print(f"An error occurred: {str(e)}")