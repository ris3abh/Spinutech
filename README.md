# Agentic system for SEO Optimization

## Overview
This project is an advanced AI-powered SEO optimization system designed to generate high-quality, SEO-optimized content using large language models and competitive analysis. The tool analyzes top-ranking search results, generates draft articles, and optimizes them based on SEO best practices and competitor insights.

## Current Capabilities

| Feature | Description |
|---------|-------------|
| SEO Landscape Analysis | Analyzes top-ranking search results for keyword density, content structure, and linking patterns |
| Content Generation | Creates draft articles with specified topics, tones, lengths, and keywords |
| SEO Optimization | Enhances content for search engines while maintaining original voice and quality |
| Competitor Analysis | Provides recommendations based on top competitors' content strategies |
| Content Caching | Stores and retrieves SEO analysis results to avoid redundant web searches |
| Multiple Output Formats | Generates articles in markdown format with SEO recommendations |

## Future Work

| Area | Description |
|------|-------------|
| Multi-Format Support | Extend SEO optimization to product descriptions, landing pages, and other content types |
| Vector Database Integration | Implement vector databases for content storage and retrieval based on semantic similarity |
| Personalization Engine | Develop style adaptation to match user's writing style and client-specific preferences |
| Advanced SEO Analysis | Incorporate entity analysis, credibility assessment, conversational search readiness, and platform presence evaluation |
| Multi-Dimensional SEO Analysis | Focus on entity optimization, Google's N-E-E-A-T-T principles, and knowledge panel readiness |
| Client-Specific Customization | Allow storage and retrieval of client-specific content information for personalized optimization |

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/ris3abh/Spinutech.git
   cd Spinutech
   ```

2. Python Virtual Env:
  ``` bash
  python -m venv venv
  source venv/bin/activate  # On Windows: venv\Scripts\activate 
  ```

3. Add your .env file and populate it with OPENAI_API_KEY

### Usage:

#### Basic Use Case:

```bash
python SEOoptimization/run.py --topic "Your Topic" --tone "professional" --length "1200 words" --keywords "keyword1, keyword2, keyword3" --debug --save
```


```bash
python SEOoptimization/run.py --topic "A Leader in Innovative Window and Door Solutions" --tone "professional" --length "1500 words" --keywords "window solutions, door technology, innovative designs, energy efficiency, architectural products" --debug --save
```


```bash
python SEOoptimization/run.py --topic "Compact Tractors for Modern Farming" --tone "professional" --length "1200 words" --keywords "compact tractors, sub-compact tractors, farming equipment, agricultural machinery, small farm solutions" --debug --save
```


```bash
python SEOoptimization/run.py --topic "Premier Provider of End-to-End Technical and Creative Film Solutions" --tone "professional" --length "1800 words" --keywords "film production services, technical solutions, creative vision, filmmaking technology, production workflow" --debug --save
```

### Command Options
--topic:	Topic of the article (required)
--tone:	Tone of the article (default: professional)
--length:	Desired article length (default: 1000 words)
--keywords:	Comma-separated keywords to include (required)
--debug:	Enable debug mode for detailed output
--save:	Save generated artifacts to files




