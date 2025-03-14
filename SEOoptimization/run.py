import sys
import os
import argparse
import json
from pathlib import Path

# Add the parent directory to the Python path to enable imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.dont_write_bytecode = True  # Prevent __pycache__ creation

# Set environment variable for tokenizers
os.environ["TOKENIZERS_PARALLELISM"] = "false"

from SEOoptimization.config.env import load_environment
from SEOoptimization.graphs.seo_workflow import run_seo_workflow

def create_output_dir():
    """Create output directory for saving artifacts."""
    output_dir = Path("seo_output")
    output_dir.mkdir(exist_ok=True)
    return output_dir

def save_artifact(content, filename, output_dir):
    """Save content to a file in the output directory."""
    filepath = output_dir / filename
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    return filepath

def main():
    """Main entry point for the SEO optimization tool."""
    # Load environment variables
    load_environment()
    
    # Create output directory
    output_dir = create_output_dir()
    
    # Set up argument parsing
    parser = argparse.ArgumentParser(description='Generate articles with customizable parameters.')
    parser.add_argument('--topic', type=str, required=True, help='Topic of the article')
    parser.add_argument('--tone', type=str, default="professional", help='Tone of the article (default: professional)')
    parser.add_argument('--length', type=str, default="1000 words", help='Length of the article (default: 1000 words)')
    parser.add_argument('--keywords', type=str, required=True, help='Keywords to include in the article (comma-separated)')
    parser.add_argument('--debug', action='store_true', help='Enable debug mode for more detailed output')
    parser.add_argument('--save', action='store_true', help='Save artifacts to files')
    
    args = parser.parse_args()
    
    try:
        print(f"\n{'='*80}\nStarting SEO Optimization for: {args.topic}\n{'='*80}\n")
        
        # Run the SEO workflow
        result = run_seo_workflow(
            topic=args.topic,
            tone=args.tone,
            length=args.length,
            keywords=args.keywords
        )
        
        # Extract all artifacts for review
        seo_analysis = result.get("seo_analysis", {})
        article_draft = result.get("article_draft", "")
        final_article = result.get("final_article", "")
        
        # Print workflow messages
        if args.debug or args.save:
            print("\n--- Workflow Messages ---\n")
            messages_text = ""
            for message in result["messages"]:
                role = "Human" if message.type == "human" else "AI"
                message_content = f"{role}: {message.content}"
                print(message_content)
                messages_text += message_content + "\n\n"
            
            # Save messages if requested
            if args.save:
                save_artifact(messages_text, "workflow_messages.txt", output_dir)
            
            if result.get("errors"):
                print("\n--- Errors ---\n")
                for error in result["errors"]:
                    print(f"- {error}")
        
        # Print SEO analysis details
        print("\n--- SEO Analysis Details ---\n")
        if seo_analysis:
            # Display key metrics
            if "avg_word_count" in seo_analysis:
                print(f"Target Word Count: {int(seo_analysis['avg_word_count'])} words")
            
            if "keyword_density" in seo_analysis:
                density = seo_analysis["keyword_density"]
                print(f"Optimal Keyword Density:")
                print(f"  - In titles: {density.get('title', 0)*100:.1f}%")
                print(f"  - In headings: {density.get('headings', 0)*100:.1f}%")
                print(f"  - In content: {density.get('content', 0):.2f}%")
            
            # Display link recommendations
            if "link_patterns" in seo_analysis:
                links = seo_analysis["link_patterns"]
                print(f"Link Recommendations:")
                print(f"  - Internal links: {int(links.get('avg_internal', 0))}")
                print(f"  - External links: {int(links.get('avg_external', 0))}")
            
            # Display analyzed URLs
            if "analyzed_urls" in seo_analysis:
                print(f"Analyzed {seo_analysis['analyzed_urls']} top-ranking URLs")
            
            # Display SEO recommendations
            if "recommendations" in seo_analysis:
                print("\nSEO Recommendations:")
                for i, rec in enumerate(seo_analysis["recommendations"], 1):
                    print(f"{i}. {rec}")
            
            # Save SEO analysis if requested
            if args.save:
                save_artifact(json.dumps(seo_analysis, indent=2), "seo_analysis.json", output_dir)
        else:
            print("No SEO analysis data available.")
        
        # Print the article draft
        if article_draft:
            print("\n--- Article Draft (Before Optimization) ---\n")
            print(article_draft)
            
            # Save article draft if requested
            if args.save:
                draft_path = save_artifact(article_draft, "article_draft.md", output_dir)
                print(f"\nArticle draft saved to: {draft_path}")
        
        # Print the final article
        if final_article:
            print("\n--- SEO Optimized Article ---\n")
            print(final_article)
            
            # Save final article if requested
            if args.save:
                final_path = save_artifact(final_article, "final_article.md", output_dir)
                print(f"\nFinal article saved to: {final_path}")
        else:
            print("\n--- No Final Article Generated ---\n")
            print("The workflow completed but did not produce a final article.")
        
        # Print keyword usage analysis
        if final_article and args.keywords:
            print("\n--- Keyword Usage Analysis ---\n")
            
            keywords_list = [k.strip() for k in args.keywords.split(',')]
            keyword_stats = {}
            
            for keyword in keywords_list:
                # Count occurrences
                count = final_article.lower().count(keyword.lower())
                
                # Check if in title (first line)
                title = final_article.split('\n')[0] if '\n' in final_article else ""
                in_title = keyword.lower() in title.lower()
                
                # Check if in headings (lines starting with #)
                in_headings = False
                headings = [line for line in final_article.split('\n') if line.strip().startswith('#')]
                for heading in headings:
                    if keyword.lower() in heading.lower():
                        in_headings = True
                        break
                
                # Store stats
                keyword_stats[keyword] = {
                    "count": count,
                    "in_title": in_title,
                    "in_headings": in_headings,
                    "density": count / len(final_article.split()) * 100 if final_article else 0
                }
            
            # Display keyword stats
            print(f"{'Keyword':<25} | {'Count':<6} | {'In Title':<8} | {'In Headings':<11} | {'Density':<8}")
            print("-" * 70)
            for keyword, stats in keyword_stats.items():
                print(f"{keyword[:25]:<25} | {stats['count']:<6} | {stats['in_title']!s:<8} | {stats['in_headings']!s:<11} | {stats['density']:.2f}%")
        
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        # Print more detailed error information if in debug mode
        if args.debug:
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    main()