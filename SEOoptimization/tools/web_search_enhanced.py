# SEOoptimization/tools/web_search_enhanced.py

import os
import requests
from bs4 import BeautifulSoup
import time
import sys
import random
from googlesearch import search
from concurrent.futures import ThreadPoolExecutor, as_completed
import numpy as np
from typing import List, Dict, Tuple, Any, Optional
from langchain_core.tools import tool

# Constants
NUM_SEARCH = 10  # Number of search results to retrieve
SEARCH_TIME_LIMIT = 10  # Timeout for each search request
MAX_CONTENT = 10000  # Max content length to process
TOTAL_TIMEOUT = 30  # Total timeout for all operations

# Import necessary models
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from rank_bm25 import BM25Okapi
import torch

from SEOoptimization.utils.model_manager import model_manager

class BM_RAGAM:
    def __init__(self):
        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        
    def compute_bm25_scores(self, query: str, documents: List[str]) -> np.ndarray:
        """Compute BM25 scores for documents."""
        if not documents:
            return np.array([])
            
        tokenized_docs = [doc.lower().split() for doc in documents]
        tokenized_query = query.lower().split()
        bm25 = BM25Okapi(tokenized_docs)
        return np.array(bm25.get_scores(tokenized_query))
    
    def compute_semantic_scores(self, query: str, documents: List[str]) -> np.ndarray:
        """Compute semantic similarity scores using transformer embeddings."""
        if not documents:
            return np.array([])
            
        # Use the model manager to get embeddings
        query_embedding = model_manager.encode_text([query], batch_size=1)
        doc_embeddings = model_manager.encode_text(documents, batch_size=8)
        
        similarities = cosine_similarity([query_embedding[0]], doc_embeddings)[0]
        return similarities
    
    def compute_attention_weights(self, bm25_scores: np.ndarray, semantic_scores: np.ndarray) -> Tuple[float, float]:
        """Compute attention weights for BM25 and semantic scores."""
        bm25_max = np.max(bm25_scores) if len(bm25_scores) > 0 else 1
        semantic_max = np.max(semantic_scores) if len(semantic_scores) > 0 else 1
        
        # Normalize scores
        bm25_norm = bm25_scores / bm25_max if bm25_max != 0 else bm25_scores
        semantic_norm = semantic_scores / semantic_max if semantic_max != 0 else semantic_scores
        
        # Compute weights using softmax
        weights = np.exp([np.mean(bm25_norm), np.mean(semantic_norm)])
        weights = weights / np.sum(weights)
        
        return weights[0], weights[1]
    
    def rank_documents(self, query: str, documents: List[str]) -> List[Tuple[int, float]]:
        """Rank documents using the hybrid approach."""
        if not documents:
            return []
            
        bm25_scores = self.compute_bm25_scores(query, documents)
        semantic_scores = self.compute_semantic_scores(query, documents)
        
        # Compute attention weights
        bm25_weight, semantic_weight = self.compute_attention_weights(bm25_scores, semantic_scores)
        
        # Combine scores using attention weights
        final_scores = (bm25_weight * bm25_scores) + (semantic_weight * semantic_scores)
        
        # Return sorted document indices and scores
        ranked_indices = np.argsort(final_scores)[::-1]
        return [(idx, final_scores[idx]) for idx in ranked_indices]

class VectorizedKnowledgeBase:
    def __init__(self):
        self.document_vectors = None
        self.documents = []
        self.urls = []
    
    def add_documents(self, documents: List[str], urls: List[str]):
        """Add documents to the knowledge base."""
        if not documents or not urls:
            return
            
        self.documents.extend(documents)
        self.urls.extend(urls)
        
        # Use the model manager to get embeddings efficiently
        new_vectors = model_manager.encode_text(documents, batch_size=8)
        
        if self.document_vectors is None:
            self.document_vectors = new_vectors
        else:
            try:
                self.document_vectors = np.vstack([self.document_vectors, new_vectors])
            except ValueError as e:
                print(f"Error combining document vectors: {e}")
                # If there's an error with vstack, ensure dimensions match
                if self.document_vectors.shape[1] == new_vectors.shape[1]:
                    print("Attempting to recover by recreating document vectors")
                    # Recreate all vectors to ensure consistency
                    self.document_vectors = model_manager.encode_text(self.documents, batch_size=8)
    
    def search(self, query: str, top_k: int = 5) -> List[Tuple[str, str, float]]:
        """Search for most relevant documents."""
        if not self.documents or self.document_vectors is None or not hasattr(self.document_vectors, 'shape'):
            return []
            
        # Use the model manager to get query embedding
        query_vector = model_manager.encode_text([query], batch_size=1)[0]
        
        # Compute similarities
        similarities = cosine_similarity([query_vector], self.document_vectors)[0]
        
        # Get top-k results
        top_indices = np.argsort(similarities)[::-1][:top_k]
        
        return [(self.urls[i], self.documents[i], similarities[i]) for i in top_indices]

def extract_main_content(soup):
    """
    Extracts the main textual content from a BeautifulSoup object by removing
    navigation, headers, footers, scripts, and styles.
    """
    # Remove unwanted elements
    for element in soup.find_all(['nav', 'header', 'footer', 'script', 'style']):
        element.decompose()
    
    # Try different strategies to locate the main content
    content = soup.find('article')
    if not content:
        content = soup.find('main')
    if not content:
        content = soup.find('div', class_=['content', 'main', 'article'])
    
    if content:
        paragraphs = content.find_all('p')
    else:
        paragraphs = soup.find_all('p')
    
    return ' '.join([para.get_text().strip() for para in paragraphs])

def extract_seo_elements(soup, url):
    """
    Extract SEO-relevant elements from a webpage.
    """
    seo_elements = {
        'url': url,
        'title': '',
        'meta_description': '',
        'headings': {
            'h1': [],
            'h2': [],
            'h3': [],
            'h4': [],
            'h5': [],
            'h6': []
        },
        'images': 0,
        'links': {
            'internal': 0,
            'external': 0
        },
        'word_count': 0,
        'schema_markup': False
    }
    
    # Extract title
    title_tag = soup.find('title')
    if title_tag and title_tag.string:
        seo_elements['title'] = title_tag.string.strip()
    
    # Extract meta description
    meta_desc = soup.find('meta', attrs={'name': 'description'})
    if meta_desc and meta_desc.get('content'):
        seo_elements['meta_description'] = meta_desc.get('content').strip()
    
    # Extract headings
    for level in range(1, 7):
        headings = soup.find_all(f'h{level}')
        seo_elements['headings'][f'h{level}'] = [h.get_text().strip() for h in headings]
    
    # Count images
    seo_elements['images'] = len(soup.find_all('img'))
    
    # Count links
    base_domain = url.split('/')[2] if url.startswith(('http://', 'https://')) else ''
    for link in soup.find_all('a', href=True):
        href = link['href']
        if href.startswith(('http://', 'https://')):
            if base_domain and base_domain in href:
                seo_elements['links']['internal'] += 1
            else:
                seo_elements['links']['external'] += 1
        else:
            seo_elements['links']['internal'] += 1
    
    # Check for schema markup
    seo_elements['schema_markup'] = bool(soup.find('script', type='application/ld+json'))
    
    # Extract content and count words
    content = extract_main_content(soup)
    seo_elements['word_count'] = len(content.split())
    
    return seo_elements

class EnhancedWebScraper:
    """
    EnhancedWebScraper integrates advanced retrieval mechanisms for SEO analysis
    """
    
    def __init__(self):
        # Initialize the BM_RAGAM retriever and the vectorized knowledge base
        self.ragam = BM_RAGAM()
        self.knowledge_base = VectorizedKnowledgeBase()
        
    def fetch_and_process_content(self, url: str, timeout: int) -> Tuple[str, str, dict]:
        """
        Fetches the webpage at `url` within the specified `timeout`, parses the HTML 
        with BeautifulSoup, and extracts the main content using `extract_main_content()`.
        
        Returns:
            A tuple (url, content, seo_elements).
        """
        # Validate URL before attempting to fetch
        if not url.startswith(('http://', 'https://')):
            print(f"Error processing {url}: Invalid URL format - missing scheme")
            return url, None, None
            
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Connection': 'keep-alive',
            }
            
            # Implement exponential backoff retry logic
            max_retries = 3
            retry_delay = 1  # Initial delay in seconds
            
            for attempt in range(max_retries):
                try:
                    response = requests.get(url, timeout=timeout, headers=headers)
                    response.raise_for_status()
                    break  # Success, exit retry loop
                except (requests.ConnectionError, requests.Timeout) as e:
                    if attempt < max_retries - 1:  # Don't sleep on the last attempt
                        retry_delay_with_jitter = retry_delay * (1 + 0.2 * random.random())
                        print(f"Attempt {attempt+1} failed for {url}: {str(e)}. Retrying in {retry_delay_with_jitter:.2f}s...")
                        time.sleep(retry_delay_with_jitter)
                        retry_delay *= 2  # Exponential backoff
                    else:
                        raise  # Re-raise the exception on the last attempt
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract main content
            content = extract_main_content(soup)
            
            # Extract SEO elements
            seo_elements = extract_seo_elements(soup, url)
            
            # Basic filtering: only accept content that is longer than 50 characters.
            if content and len(content) > 50:
                return url, content, seo_elements
            else:
                print(f"Content too short or not found for {url}")
                return url, None, None
                
        except requests.exceptions.RequestException as e:
            print(f"Request error processing {url}: {str(e)}")
            return url, None, None
        except Exception as e:
            print(f"Unexpected error processing {url}: {str(e)}")
            return url, None, None

    def parse_google_results(self, query: str, num_search: int = NUM_SEARCH) -> Tuple[Dict[str, str], List[Dict]]:
        """
        Performs a Google search using the query and returns a dictionary 
        mapping each URL to its extracted content along with SEO analysis.
        """
        # Step 1: Get initial URLs from Google
        try:
            # Add sleep before search to reduce chance of being blocked
            time.sleep(1)
            
            # Ensure query is properly formatted
            safe_query = query.strip()
            if not safe_query:
                raise ValueError("Empty search query")
                
            print(f"Searching for: {safe_query}")
            urls = list(search(safe_query, num_results=num_search))
            
            # Validate URLs
            valid_urls = []
            for url in urls:
                if url and isinstance(url, str) and url.startswith(('http://', 'https://')):
                    valid_urls.append(url)
                else:
                    print(f"Skipping invalid URL: {url}")
            
            urls = valid_urls
            print(f"Found {len(urls)} valid search results")
            
        except Exception as e:
            print(f"Error in Google search: {e}")
            urls = []
        
        if not urls:
            print("No valid URLs found from search results")
            return {}, []
            
        # Step 2: Fetch webpage content concurrently
        results = []
        seo_analyses = []
        
        with ThreadPoolExecutor(max_workers=5) as executor:
            future_to_url = {
                executor.submit(self.fetch_and_process_content, url, SEARCH_TIME_LIMIT): url 
                for url in urls
            }
            for future in as_completed(future_to_url):
                try:
                    url, content, seo_elements = future.result()
                    if content and seo_elements:
                        results.append((url, content))
                        seo_analyses.append(seo_elements)
                except Exception as e:
                    print(f"Error processing {future_to_url[future]}: {e}")
        
        if not results:
            return {}, []
        
        # Unpack URLs and contents from the results
        urls_list, contents = zip(*results)
        
        # Step 3: Add the fetched documents to the vectorized knowledge base.
        self.knowledge_base.add_documents(list(contents), list(urls_list))
        
        # Step 4: Rank the documents using BM_RAGAM
        ranked_results = self.ragam.rank_documents(query, list(contents))
        
        # Step 5: Filter results based on a relevance threshold.
        relevance_threshold = 0.3
        filtered_results = {}
        ranked_seo_analyses = []
        
        for idx, score in ranked_results:
            if score > relevance_threshold:
                filtered_results[urls_list[idx]] = contents[idx]
                # Find the corresponding SEO analysis and add the relevance score
                for analysis in seo_analyses:
                    if analysis['url'] == urls_list[idx]:
                        analysis['relevance_score'] = float(score)
                        ranked_seo_analyses.append(analysis)
                        break
                
        return filtered_results, ranked_seo_analyses

from SEOoptimization.utils.cache import SEOCache

class SEOAnalyzer:
    """
    Analyzes and extracts SEO insights from web content
    """
    
    def __init__(self, use_cache: bool = True):
        self.scraper = EnhancedWebScraper()
        self.cache = SEOCache() if use_cache else None
    
    def analyze_keyword(self, keyword: str, num_results: int = 10, force_refresh: bool = False) -> Dict[str, Any]:
        """
        Analyzes search results for a specific keyword and returns SEO insights.
        
        Args:
            keyword: The keyword or query to analyze
            num_results: Number of search results to analyze
            force_refresh: Whether to force a fresh analysis (ignore cache)
            
        Returns:
            Dictionary containing SEO insights and recommendations
        """
        # Check cache first if enabled and not forcing refresh
        if self.cache and not force_refresh:
            cached_results = self.cache.get(keyword)
            if cached_results:
                print(f"Using cached SEO analysis for: {keyword}")
                return cached_results
        
        print(f"Performing fresh SEO analysis for: {keyword}")
        
        # Search for the keyword
        content_dict, seo_analyses = self.scraper.parse_google_results(keyword, num_results)
        
        if not content_dict or not seo_analyses:
            results = {
                "keyword": keyword,
                "error": "No valid search results found",
                "recommendations": []
            }
        else:
            # Analyze search results for SEO patterns
            results = self._extract_seo_insights(keyword, content_dict, seo_analyses)
        
        # Cache the results if caching is enabled
        if self.cache:
            self.cache.set(keyword, results)
        
        return results
    
    def _extract_seo_insights(self, keyword: str, content_dict: Dict[str, str], seo_analyses: List[Dict]) -> Dict[str, Any]:
        """
        Extracts SEO insights from the search results.
        """
        # Initialize insights structure
        insights = {
            "keyword": keyword,
            "analyzed_urls": len(content_dict),
            "avg_word_count": 0,
            "title_patterns": [],
            "heading_patterns": [],
            "keyword_density": {
                "avg": 0,
                "title": 0,
                "headings": 0,
                "content": 0
            },
            "link_patterns": {
                "avg_internal": 0,
                "avg_external": 0
            },
            "recommendations": []
        }
        
        # Skip if no results
        if not seo_analyses:
            return insights
        
        # Calculate averages
        word_counts = [analysis['word_count'] for analysis in seo_analyses]
        insights["avg_word_count"] = sum(word_counts) / len(word_counts) if word_counts else 0
        
        internal_links = [analysis['links']['internal'] for analysis in seo_analyses]
        external_links = [analysis['links']['external'] for analysis in seo_analyses]
        insights["link_patterns"]["avg_internal"] = sum(internal_links) / len(internal_links) if internal_links else 0
        insights["link_patterns"]["avg_external"] = sum(external_links) / len(external_links) if external_links else 0
        
        # Extract title patterns
        title_keywords = []
        for analysis in seo_analyses:
            title = analysis['title'].lower()
            if keyword.lower() in title:
                title_keywords.append(True)
            else:
                title_keywords.append(False)
        
        insights["keyword_density"]["title"] = sum(title_keywords) / len(title_keywords) if title_keywords else 0
        
        # Extract heading patterns
        heading_keywords = []
        for analysis in seo_analyses:
            has_keyword = False
            for level in ['h1', 'h2', 'h3']:
                for heading in analysis['headings'][level]:
                    if keyword.lower() in heading.lower():
                        has_keyword = True
                        break
                if has_keyword:
                    break
            heading_keywords.append(has_keyword)
        
        insights["keyword_density"]["headings"] = sum(heading_keywords) / len(heading_keywords) if heading_keywords else 0
        
        # Calculate content keyword density
        keyword_counts = []
        for url, content in content_dict.items():
            if content:
                keyword_count = content.lower().count(keyword.lower())
                word_count = len(content.split())
                if word_count > 0:
                    keyword_counts.append(keyword_count / word_count * 100)  # Percentage
        
        insights["keyword_density"]["content"] = sum(keyword_counts) / len(keyword_counts) if keyword_counts else 0
        insights["keyword_density"]["avg"] = (
            insights["keyword_density"]["title"] + 
            insights["keyword_density"]["headings"] + 
            insights["keyword_density"]["content"]
        ) / 3
        
        # Generate recommendations
        insights["recommendations"] = self._generate_recommendations(insights, seo_analyses)
        
        return insights
    
    def _generate_recommendations(self, insights: Dict[str, Any], seo_analyses: List[Dict]) -> List[str]:
        """
        Generate SEO recommendations based on the analysis.
        """
        recommendations = []
        keyword = insights["keyword"]
        
        # Word count recommendations
        if insights["avg_word_count"] > 0:
            recommendations.append(f"Target word count: {int(insights['avg_word_count'])} words based on top-ranking pages")
        
        # Title recommendations
        if insights["keyword_density"]["title"] > 0.7:
            recommendations.append(f"Include the keyword '{keyword}' in your title - {int(insights['keyword_density']['title'] * 100)}% of top pages do this")
        
        # Heading recommendations
        if insights["keyword_density"]["headings"] > 0.5:
            recommendations.append(f"Include the keyword '{keyword}' in at least one heading - {int(insights['keyword_density']['headings'] * 100)}% of top pages do this")
        
        # Keyword density recommendations
        if insights["keyword_density"]["content"] > 0:
            recommendations.append(f"Aim for a keyword density of approximately {insights['keyword_density']['content']:.2f}% in your content")
        
        # Link recommendations
        if insights["link_patterns"]["avg_internal"] > 0:
            recommendations.append(f"Include approximately {int(insights['link_patterns']['avg_internal'])} internal links")
        
        if insights["link_patterns"]["avg_external"] > 0:
            recommendations.append(f"Include approximately {int(insights['link_patterns']['avg_external'])} external links to authoritative sources")
        
        # Structure recommendations based on top results
        top_analysis = seo_analyses[0] if seo_analyses else None
        if top_analysis:
            h1_count = len(top_analysis['headings']['h1'])
            h2_count = len(top_analysis['headings']['h2'])
            h3_count = len(top_analysis['headings']['h3'])
            
            if h1_count > 0:
                recommendations.append(f"Use {h1_count} H1 tag(s) - the top result does this")
            
            if h2_count > 0:
                recommendations.append(f"Structure your content with approximately {h2_count} H2 sections")
            
            if h3_count > 0:
                recommendations.append(f"Further organize content with {h3_count} H3 subsections")
        
        return recommendations

# Function for direct use in the graph
def analyze_keyword_direct(topic: str, keywords: str, force_refresh: bool = False) -> Dict[str, Any]:
    """
    Analyze a keyword or topic for SEO insights (for use in the workflow graph).
    
    Args:
        topic: The main topic to analyze
        keywords: Comma-separated list of keywords
        force_refresh: Whether to force a fresh analysis (ignore cache)
        
    Returns:
        Dictionary containing SEO insights and recommendations
    """
    analyzer = SEOAnalyzer(use_cache=True)
    
    # Combine topic and main keyword for search
    primary_keyword = keywords.split(',')[0].strip()
    search_query = f"{topic} {primary_keyword}"
    
    print(f"Analyzing SEO landscape for: {search_query}")
    
    # Perform analysis
    analysis_results = analyzer.analyze_keyword(search_query, force_refresh=force_refresh)
    
    # Add topic and keywords to results
    analysis_results["topic"] = topic
    analysis_results["keywords"] = keywords
    
    # Add timestamp
    analysis_results["timestamp"] = time.time()
    
    return analysis_results

@tool
def analyze_keyword(topic_and_keywords: str) -> str:
    """
    Analyze a keyword or topic for SEO insights. Format: 'topic | keywords'
    Example: 'machine learning best practices | AI, neural networks, deep learning'
    """
    parts = topic_and_keywords.split('|')
    if len(parts) != 2:
        return "Error: Input must be in format 'topic | keywords'"
    
    topic = parts[0].strip()
    keywords = parts[1].strip()
    
    analyzer = SEOAnalyzer()
    search_query = f"{topic} {keywords.split(',')[0].strip()}"
    results = analyzer.analyze_keyword(search_query)
    
    # Format the results as a readable string
    output = f"SEO Analysis for: {search_query}\n\n"
    output += f"Analyzed {results['analyzed_urls']} top-ranking pages\n"
    output += f"Average word count: {int(results['avg_word_count'])} words\n\n"
    
    output += "Keyword Density:\n"
    output += f"- In titles: {results['keyword_density']['title']*100:.1f}%\n"
    output += f"- In headings: {results['keyword_density']['headings']*100:.1f}%\n"
    output += f"- In content: {results['keyword_density']['content']:.2f}%\n\n"
    
    output += "Link Patterns:\n"
    output += f"- Average internal links: {int(results['link_patterns']['avg_internal'])}\n"
    output += f"- Average external links: {int(results['link_patterns']['avg_external'])}\n\n"
    
    output += "SEO Recommendations:\n"
    for i, rec in enumerate(results['recommendations'], 1):
        output += f"{i}. {rec}\n"
    
    return output