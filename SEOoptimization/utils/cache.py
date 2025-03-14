# SEOoptimization/utils/cache.py

import os
import json
import hashlib
import time
from typing import Dict, Any, Optional
from pathlib import Path

class SEOCache:
    """
    Cache for SEO analysis results to reduce repeated web searches.
    Implements a disk-based cache with TTL (time-to-live) for entries.
    """
    
    def __init__(self, cache_dir: str = ".seo_cache", ttl_days: int = 7):
        """
        Initialize the cache.
        
        Args:
            cache_dir: Directory to store cache files
            ttl_days: Time-to-live for cache entries in days
        """
        self.cache_dir = Path(cache_dir)
        self.ttl_seconds = ttl_days * 24 * 60 * 60
        
        # Create cache directory if it doesn't exist
        if not self.cache_dir.exists():
            self.cache_dir.mkdir(parents=True)
    
    def _get_cache_key(self, query: str) -> str:
        """
        Generate a cache key for a query.
        
        Args:
            query: Search query string
            
        Returns:
            MD5 hash of the query as a hex string
        """
        # Normalize the query (lowercase, trim whitespace)
        normalized_query = query.lower().strip()
        
        # Generate MD5 hash
        return hashlib.md5(normalized_query.encode('utf-8')).hexdigest()
    
    def _get_cache_path(self, cache_key: str) -> Path:
        """
        Get the file path for a cache key.
        
        Args:
            cache_key: Cache key string
            
        Returns:
            Path object for the cache file
        """
        return self.cache_dir / f"{cache_key}.json"
    
    def get(self, query: str) -> Optional[Dict[str, Any]]:
        """
        Get cached results for a query if available and not expired.
        
        Args:
            query: Search query string
            
        Returns:
            Cached results or None if not found or expired
        """
        cache_key = self._get_cache_key(query)
        cache_path = self._get_cache_path(cache_key)
        
        # Check if cache file exists
        if not cache_path.exists():
            return None
        
        try:
            # Read cache file
            with open(cache_path, 'r', encoding='utf-8') as f:
                cache_data = json.load(f)
            
            # Check if cache is expired
            timestamp = cache_data.get('timestamp', 0)
            if time.time() - timestamp > self.ttl_seconds:
                print(f"Cache expired for query: {query}")
                return None
            
            print(f"Cache hit for query: {query}")
            return cache_data.get('data')
            
        except (json.JSONDecodeError, KeyError) as e:
            print(f"Error reading cache: {e}")
            return None
    
    def set(self, query: str, data: Dict[str, Any]) -> None:
        """
        Store results in the cache.
        
        Args:
            query: Search query string
            data: Data to cache
        """
        cache_key = self._get_cache_key(query)
        cache_path = self._get_cache_path(cache_key)
        
        try:
            # Prepare cache data with timestamp
            cache_data = {
                'timestamp': time.time(),
                'query': query,
                'data': data
            }
            
            # Write to cache file
            with open(cache_path, 'w', encoding='utf-8') as f:
                json.dump(cache_data, f, indent=2)
                
            print(f"Cache set for query: {query}")
            
        except Exception as e:
            print(f"Error writing to cache: {e}")
    
    def invalidate(self, query: Optional[str] = None) -> None:
        """
        Invalidate cache entries.
        
        Args:
            query: Query to invalidate, or None to invalidate all entries
        """
        if query is None:
            # Invalidate all cache entries
            for cache_file in self.cache_dir.glob('*.json'):
                try:
                    cache_file.unlink()
                except Exception as e:
                    print(f"Error removing cache file {cache_file}: {e}")
            print("All cache entries invalidated")
        else:
            # Invalidate specific query
            cache_key = self._get_cache_key(query)
            cache_path = self._get_cache_path(cache_key)
            
            if cache_path.exists():
                try:
                    cache_path.unlink()
                    print(f"Cache invalidated for query: {query}")
                except Exception as e:
                    print(f"Error removing cache file for query {query}: {e}")
    
    def clean_expired(self) -> int:
        """
        Clean expired cache entries.
        
        Returns:
            Number of entries cleaned
        """
        cleaned_count = 0
        
        for cache_file in self.cache_dir.glob('*.json'):
            try:
                with open(cache_file, 'r', encoding='utf-8') as f:
                    cache_data = json.load(f)
                
                timestamp = cache_data.get('timestamp', 0)
                if time.time() - timestamp > self.ttl_seconds:
                    cache_file.unlink()
                    cleaned_count += 1
            except Exception as e:
                print(f"Error checking cache file {cache_file}: {e}")
                # Remove invalid cache files
                try:
                    cache_file.unlink()
                    cleaned_count += 1
                except:
                    pass
        
        if cleaned_count > 0:
            print(f"Cleaned {cleaned_count} expired cache entries")
        
        return cleaned_count