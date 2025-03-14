import sys
import os
import argparse

# Add the parent directory to the Python path to enable imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.dont_write_bytecode = True  # Prevent __pycache__ creation

from SEOoptimization.config.env import load_environment
from SEOoptimization.graphs.seo_workflow import run_seo_workflow

def main():
    """Main entry point for the SEO optimization tool."""
    # Load environment variables
    load_environment()
    
    # Set up argument parsing
    parser = argparse.ArgumentParser(description='Generate articles with customizable parameters.')
    parser.add_argument('--topic', type=str, required=True, help='Topic of the article')
    parser.add_argument('--tone', type=str, default="professional", help='Tone of the article (default: professional)')
    parser.add_argument('--length', type=str, default="1000 words", help='Length of the article (default: 1000 words)')
    parser.add_argument('--keywords', type=str, required=True, help='Keywords to include in the article (comma-separated)')
    parser.add_argument('--debug', action='store_true', help='Enable debug mode for more detailed output')
    
    args = parser.parse_args()
    
    try:
        # Run the SEO workflow
        result = run_seo_workflow(
            topic=args.topic,
            tone=args.tone,
            length=args.length,
            keywords=args.keywords
        )
        
        # Print debug information if requested
        if args.debug:
            print("\n--- Workflow Messages ---\n")
            for message in result["messages"]:
                role = "Human" if message.type == "human" else "AI"
                print(f"{role}: {message.content}")
            
            if result.get("errors"):
                print("\n--- Errors ---\n")
                for error in result["errors"]:
                    print(f"- {error}")
        
        # Print the final article
        if result.get("final_article"):
            print("\n--- SEO Optimized Article ---\n")
            print(result["final_article"])
        elif result.get("article_draft"):
            print("\n--- Article Draft (Not Optimized) ---\n")
            print(result["article_draft"])
        else:
            print("\n--- No Article Generated ---\n")
            print("The workflow completed but did not produce an article.")
        
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        # Print more detailed error information if in debug mode
        if args.debug:
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    main()