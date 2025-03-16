"""
Test script for the enhanced workflow.
This script allows testing the enhanced workflow with different content types.
"""

import os
import sys
import json
import time
import argparse
from pathlib import Path

# Add the parent directory to the Python path to enable imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.dont_write_bytecode = True  # Prevent __pycache__ creation

# Set environment variable for tokenizers
os.environ["TOKENIZERS_PARALLELISM"] = "false"

from SEOoptimization.config.env import load_environment
from SEOoptimization.graphs.enhanced_workflow import run_enhanced_workflow
from SEOoptimization.api_bridge import (
    generate_content_api,
    analyze_seo_api,
    analyze_style_api,
    analyze_client_api,
    start_file_monitoring
)

def create_output_dir():
    """Create output directory for saving artifacts."""
    output_dir = Path("enhanced_seo_output")
    output_dir.mkdir(exist_ok=True)
    return output_dir

def save_artifact(content, filename, output_dir):
    """Save content to a file in the output directory."""
    filepath = output_dir / filename
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    return filepath

def main():
    """Main function to test the enhanced workflow."""
    # Load environment variables
    load_environment()
    
    # Create output directory
    output_dir = create_output_dir()
    
    # Set up argument parsing
    parser = argparse.ArgumentParser(description='Test the enhanced SEO optimization tools.')
    subparsers = parser.add_subparsers(dest='command', help='Command to run')
    
    # Generate content command
    generate_parser = subparsers.add_parser('generate', help='Generate content with the enhanced workflow')
    generate_parser.add_argument('--topic', type=str, required=True, help='Content topic')
    generate_parser.add_argument('--tone', type=str, default="professional", help='Tone of the content (default: professional)')
    generate_parser.add_argument('--length', type=str, default="1000 words", help='Length of the content (default: 1000 words)')
    generate_parser.add_argument('--keywords', type=str, required=True, help='Keywords to include in the content (comma-separated)')
    generate_parser.add_argument('--content-type', type=str, default="article", choices=["article", "landing_page", "journal", "success_story"], help='Type of content to generate (default: article)')
    generate_parser.add_argument('--client-id', type=str, help='Optional client ID for personalization')
    generate_parser.add_argument('--specialist-id', type=str, help='Optional specialist ID for style adaptation')
    generate_parser.add_argument('--reference-files', type=str, help='Optional comma-separated list of reference files')
    generate_parser.add_argument('--debug', action='store_true', help='Enable debug mode for more detailed output')
    generate_parser.add_argument('--save', action='store_true', help='Save artifacts to files')
    generate_parser.add_argument('--api', action='store_true', help='Use the API bridge instead of direct workflow')
    generate_parser.add_argument('--start-monitoring', action='store_true', help='Start file monitoring system')
    
    # Analyze SEO command
    seo_parser = subparsers.add_parser('analyze-seo', help='Analyze SEO for a topic and keywords')
    seo_parser.add_argument('--topic', type=str, required=True, help='Content topic')
    seo_parser.add_argument('--keywords', type=str, required=True, help='Keywords to analyze (comma-separated)')
    seo_parser.add_argument('--force-refresh', action='store_true', help='Force refresh the analysis cache')
    seo_parser.add_argument('--save', action='store_true', help='Save artifacts to files')
    
    # Analyze specialist style command
    style_parser = subparsers.add_parser('analyze-style', help='Analyze specialist writing style')
    style_parser.add_argument('--specialist-id', type=str, required=True, help='Specialist ID')
    style_parser.add_argument('--reference-files', type=str, help='Optional comma-separated list of reference files')
    style_parser.add_argument('--save', action='store_true', help='Save artifacts to files')
    
    # Analyze client content command
    client_parser = subparsers.add_parser('analyze-client', help='Analyze client content patterns')
    client_parser.add_argument('--client-id', type=str, required=True, help='Client ID')
    client_parser.add_argument('--specialist-id', type=str, required=True, help='Specialist ID')
    client_parser.add_argument('--reference-files', type=str, help='Optional comma-separated list of reference files')
    client_parser.add_argument('--save', action='store_true', help='Save artifacts to files')
    
    # File monitoring command
    monitor_parser = subparsers.add_parser('start-monitoring', help='Start file monitoring system')
    
    # Default command if none specified
    if len(sys.argv) == 1:
        parser.print_help(sys.stderr)
        sys.exit(1)
        
    args = parser.parse_args()
    
    try:
        # Create output directory
        output_dir = create_output_dir()
        
        # Handle file monitoring command
        if args.command == 'start-monitoring':
            print("Starting file monitoring system...")
            if start_file_monitoring():
                print("File monitoring started successfully. Press Ctrl+C to stop.")
                try:
                    while True:
                        time.sleep(1)
                except KeyboardInterrupt:
                    print("Stopping file monitoring...")
                    return
            else:
                print("Failed to start file monitoring.")
                return
        
        # Handle analyze-seo command
        elif args.command == 'analyze-seo':
            print(f"\n{'='*80}\nAnalyzing SEO for: {args.topic} | Keywords: {args.keywords}\n{'='*80}\n")
            
            # Run SEO analysis
            seo_analysis = analyze_seo_api(
                topic=args.topic,
                keywords=args.keywords,
                force_refresh=args.force_refresh
            )
            
            # Check for errors
            if "error" in seo_analysis:
                print(f"Error: {seo_analysis['error']}")
                return
            
            # Save SEO analysis if requested
            if args.save:
                save_artifact(json.dumps(seo_analysis, indent=2), "seo_analysis.json", output_dir)
                print(f"SEO analysis saved to: {output_dir}/seo_analysis.json")
            
            # Display results
            print("\n--- SEO Analysis Results ---\n")
            
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
        
        # Handle analyze-style command
        elif args.command == 'analyze-style':
            print(f"\n{'='*80}\nAnalyzing Writing Style for: {args.specialist_id}\n{'='*80}\n")
            
            # Parse reference files if provided
            reference_files = None
            if args.reference_files:
                reference_files = [f.strip() for f in args.reference_files.split(',')]
                print(f"Including reference files: {reference_files}")
            
            # Run style analysis
            style_analysis = analyze_style_api(
                specialist_id=args.specialist_id,
                file_paths=reference_files
            )
            
            # Check for errors
            if "error" in style_analysis:
                print(f"Error: {style_analysis['error']}")
                return
            
            # Save style analysis if requested
            if args.save:
                save_artifact(json.dumps(style_analysis, indent=2), "specialist_style.json", output_dir)
                print(f"Style analysis saved to: {output_dir}/specialist_style.json")
            
            # Display results
            print("\n--- Writing Style Analysis Results ---\n")
            
            for key, value in style_analysis.items():
                if key not in ["timestamp", "specialist_id"] and value and value != "unknown":
                    print(f"{key.replace('_', ' ').title()}: {value}")
        
        # Handle analyze-client command
        elif args.command == 'analyze-client':
            print(f"\n{'='*80}\nAnalyzing Client Content for: {args.client_id}\n{'='*80}\n")
            
            # Parse reference files if provided
            reference_files = None
            if args.reference_files:
                reference_files = [f.strip() for f in args.reference_files.split(',')]
                print(f"Including reference files: {reference_files}")
            
            # Run client analysis
            client_analysis = analyze_client_api(
                client_id=args.client_id,
                specialist_id=args.specialist_id,
                file_paths=reference_files
            )
            
            # Check for errors
            if "error" in client_analysis:
                print(f"Error: {client_analysis['error']}")
                return
            
            # Save client analysis if requested
            if args.save:
                save_artifact(json.dumps(client_analysis, indent=2), "client_context.json", output_dir)
                print(f"Client analysis saved to: {output_dir}/client_context.json")
            
            # Display results
            print("\n--- Client Content Analysis Results ---\n")
            
            if "tone" in client_analysis and client_analysis["tone"] != "unknown":
                print(f"Preferred Tone: {client_analysis['tone']}")
            
            if "target_audience" in client_analysis and client_analysis["target_audience"]:
                print(f"Target Audience: {', '.join(client_analysis['target_audience'])}")
            
            if "industry_terms" in client_analysis and client_analysis["industry_terms"]:
                print(f"Industry Terms: {', '.join(client_analysis['industry_terms'][:5])}")
                if len(client_analysis["industry_terms"]) > 5:
                    print(f"  (and {len(client_analysis['industry_terms']) - 5} more)")
            
            if "key_themes" in client_analysis and client_analysis["key_themes"]:
                print(f"Key Themes: {', '.join(client_analysis['key_themes'])}")
            
            if "taboo_topics" in client_analysis and client_analysis["taboo_topics"]:
                print(f"Taboo Topics: {', '.join(client_analysis['taboo_topics'])}")
            
            if "overall_analysis" in client_analysis and client_analysis["overall_analysis"] and client_analysis["overall_analysis"] != "unknown":
                print(f"\nOverall Analysis: {client_analysis['overall_analysis']}")
        
        # Handle generate command
        elif args.command == 'generate':
            # Start file monitoring if requested
            if args.start_monitoring:
                print("Starting file monitoring system...")
                start_file_monitoring()
            
            print(f"\n{'='*80}\nGenerating {args.content_type}: {args.topic}\n{'='*80}\n")
            
            # Parse reference files if provided
            reference_files = None
            if args.reference_files:
                reference_files = [f.strip() for f in args.reference_files.split(',')]
            
            # Run the content generation
            if args.api:
                # Use the API bridge
                result = generate_content_api(
                    topic=args.topic,
                    tone=args.tone,
                    length=args.length,
                    keywords=args.keywords,
                    content_type=args.content_type,
                    client_id=args.client_id,
                    specialist_id=args.specialist_id,
                    reference_files=reference_files
                )
                
                # Extract results
                content_draft = result.get("content_draft", "")
                adapted_content = result.get("adapted_content", "")
                final_content = result.get("final_content", "")
                validation_report = result.get("validation_report", {})
                messages = result.get("messages", [])
                seo_analysis = result.get("seo_analysis", {})
                client_context = result.get("client_context", {})
                specialist_style = result.get("specialist_style", {})
                
            else:
                # Use direct workflow
                result = run_enhanced_workflow(
                    topic=args.topic,
                    tone=args.tone,
                    length=args.length,
                    keywords=args.keywords,
                    content_type=args.content_type,
                    client_id=args.client_id,
                    specialist_id=args.specialist_id
                )
                
                # Extract results
                content_draft = result.get("content_draft", "")
                adapted_content = result.get("adapted_content", "")
                final_content = result.get("final_content", "")
                validation_report = result.get("validation_report", {})
                messages = result.get("messages", [])
                seo_analysis = result.get("seo_analysis", {})
                client_context = result.get("client_context", {})
                specialist_style = result.get("specialist_style", {})
            
            # Print workflow messages
            if args.debug or args.save:
                print("\n--- Workflow Messages ---\n")
                messages_text = ""
                
                if args.api:
                    # Format is different for API bridge
                    for message in messages:
                        messages_text += f"{message}\n\n"
                        print(message)
                else:
                    for message in messages:
                        role = "Human" if message.type == "human" else "AI"
                        message_content = f"{role}: {message.content}"
                        messages_text += message_content + "\n\n"
                        print(message_content)
                
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
                # Save SEO analysis if requested
                if args.save:
                    save_artifact(json.dumps(seo_analysis, indent=2), "seo_analysis.json", output_dir)
                
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
            else:
                print("No SEO analysis data available.")
                
            # Print client context if available
            if client_context and (args.debug or args.save):
                print("\n--- Client Context ---\n")
                
                # Save client context if requested
                if args.save:
                    save_artifact(json.dumps(client_context, indent=2), "client_context.json", output_dir)
                
                # Display key elements
                if "tone" in client_context and client_context["tone"] != "unknown":
                    print(f"Preferred Tone: {client_context['tone']}")
                
                if "target_audience" in client_context and client_context["target_audience"]:
                    print(f"Target Audience: {', '.join(client_context['target_audience'])}")
                
                if "industry_terms" in client_context and client_context["industry_terms"]:
                    print(f"Industry Terms: {', '.join(client_context['industry_terms'][:5])}")
                    if len(client_context["industry_terms"]) > 5:
                        print(f"  (and {len(client_context['industry_terms']) - 5} more)")
                
                if "key_themes" in client_context and client_context["key_themes"]:
                    print(f"Key Themes: {', '.join(client_context['key_themes'])}")
                
                if "taboo_topics" in client_context and client_context["taboo_topics"]:
                    print(f"Taboo Topics: {', '.join(client_context['taboo_topics'])}")
            
            # Print specialist style if available
            if specialist_style and (args.debug or args.save):
                print("\n--- Specialist Writing Style ---\n")
                
                # Save specialist style if requested
                if args.save:
                    save_artifact(json.dumps(specialist_style, indent=2), "specialist_style.json", output_dir)
                
                # Display key elements
                for key, value in specialist_style.items():
                    if key != "overall_style" and value and value != "unknown":
                        print(f"{key.replace('_', ' ').title()}: {value}")
            
            # Print the content draft
            if content_draft and (args.debug or args.save):
                print("\n--- Content Draft (Before Style Adaptation) ---\n")
                if args.debug:
                    print(content_draft)
                else:
                    print(f"Content draft generated with {len(content_draft.split())} words")
                
                # Save content draft if requested
                if args.save:
                    draft_path = save_artifact(content_draft, f"{args.content_type}_draft.md", output_dir)
                    print(f"\nContent draft saved to: {draft_path}")
            
            # Print the adapted content
            if adapted_content and adapted_content != content_draft and (args.debug or args.save):
                print("\n--- Adapted Content (After Style Adaptation) ---\n")
                if args.debug:
                    print(adapted_content)
                else:
                    print(f"Content adapted with {len(adapted_content.split())} words")
                
                # Save adapted content if requested
                if args.save:
                    adapted_path = save_artifact(adapted_content, f"{args.content_type}_adapted.md", output_dir)
                    print(f"\nAdapted content saved to: {adapted_path}")
            
            # Print the final content
            if final_content:
                print("\n--- Final Content (SEO Optimized) ---\n")
                if not args.debug:
                    print(f"Final {args.content_type} generated with {len(final_content.split())} words")
                else:
                    print(final_content)
                
                # Save final content if requested
                if args.save:
                    final_path = save_artifact(final_content, f"{args.content_type}_final.md", output_dir)
                    print(f"\nFinal content saved to: {final_path}")
            else:
                print("\n--- No Final Content Generated ---\n")
                print("The workflow completed but did not produce final content.")
            
            # Print validation report
            if validation_report and (args.debug or args.save):
                print("\n--- Content Validation Report ---\n")
                
                # Save validation report if requested
                if args.save:
                    save_artifact(json.dumps(validation_report, indent=2), "validation_report.json", output_dir)
                
                # Display key metrics
                if "validation" in validation_report:
                    validation = validation_report["validation"]
                    
                    if "seo_score" in validation:
                        print(f"SEO Score: {validation['seo_score']}/100")
                    
                    if "content_quality_score" in validation:
                        print(f"Content Quality Score: {validation['content_quality_score']}/100")
                    
                    if "recommendations" in validation and validation["recommendations"]:
                        print("\nImprovement Recommendations:")
                        for i, rec in enumerate(validation["recommendations"], 1):
                            print(f"{i}. {rec}")
                
                if "metrics" in validation_report:
                    metrics = validation_report["metrics"]
                    
                    if "word_count" in metrics:
                        print(f"\nWord Count: {metrics['word_count']} words")
                    
                    if "heading_counts" in metrics:
                        heading_counts = metrics["heading_counts"]
                        print("Heading Structure:")
                        for level, count in heading_counts.items():
                            if count > 0:
                                print(f"  - {level.upper()}: {count}")
            
            # Print keyword usage analysis
            if final_content and args.keywords:
                print("\n--- Keyword Usage Analysis ---\n")
                
                keywords_list = [k.strip() for k in args.keywords.split(',')]
                keyword_stats = {}
                
                for keyword in keywords_list:
                    # Skip empty keywords
                    if not keyword:
                        continue
                        
                    # Count occurrences
                    count = final_content.lower().count(keyword.lower())
                    
                    # Check if in title (first line)
                    title = final_content.split('\n')[0] if '\n' in final_content else ""
                    in_title = keyword.lower() in title.lower()
                    
                    # Check if in headings (lines starting with #)
                    in_headings = False
                    headings = [line for line in final_content.split('\n') if line.strip().startswith('#')]
                    for heading in headings:
                        if keyword.lower() in heading.lower():
                            in_headings = True
                            break
                    
                    # Calculate density
                    word_count = len(final_content.split())
                    density = count / word_count * 100 if word_count else 0
                    
                    # Store stats
                    keyword_stats[keyword] = {
                        "count": count,
                        "in_title": in_title,
                        "in_headings": in_headings,
                        "density": density
                    }
                
                # Display keyword stats
                print(f"{'Keyword':<25} | {'Count':<6} | {'In Title':<8} | {'In Headings':<11} | {'Density':<8}")
                print("-" * 70)
                for keyword, stats in keyword_stats.items():
                    print(f"{keyword[:25]:<25} | {stats['count']:<6} | {stats['in_title']!s:<8} | {stats['in_headings']!s:<11} | {stats['density']:.2f}%")
        
        else:
            print("No command specified. Use --help to see available commands.")
            
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        # Print more detailed error information if in debug mode
        if hasattr(args, 'debug') and args.debug:
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    main()