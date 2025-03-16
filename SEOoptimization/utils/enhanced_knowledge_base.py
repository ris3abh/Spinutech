"""
Enhanced knowledge base for client and specialist content analysis.
This module provides a vector database for storing and retrieving documents,
and functions for analyzing writing style and client preferences.
"""

import os
import json
from typing import List, Dict, Any, Optional, Tuple
import numpy as np
from pathlib import Path

# Langchain imports
from langchain_community.document_loaders import TextLoader, PyPDFLoader, Docx2txtLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.documents import Document

# Project imports
from SEOoptimization.models.openai import initialize_llm
from SEOoptimization.utils.cache import SEOCache

class EnhancedKnowledgeBase:
    """Enhanced knowledge base for client and specialist content analysis."""
    
    def __init__(self, persist_directory: str = ".kb_cache"):
        """
        Initialize the knowledge base.
        
        Args:
            persist_directory: Directory to persist the vector database
        """
        self.persist_directory = persist_directory
        self.cache = SEOCache(cache_dir=".kb_cache", ttl_days=30)
        
        # Initialize embeddings model
        self.embeddings = HuggingFaceEmbeddings(
            model_name="all-MiniLM-L6-v2",
            model_kwargs={'device': 'cpu'},
            encode_kwargs={'normalize_embeddings': True}
        )
        
        self.vector_db = None
        self.document_sources = {}
        self.initialize_db()
    
    def initialize_db(self):
        """Initialize or load the vector database."""
        os.makedirs(self.persist_directory, exist_ok=True)
        
        try:
            if os.path.exists(os.path.join(self.persist_directory, "chroma.sqlite3")):
                print(f"Loading existing vector database from {self.persist_directory}")
                self.vector_db = Chroma(
                    persist_directory=self.persist_directory,
                    embedding_function=self.embeddings
                )
            else:
                print(f"Creating new vector database in {self.persist_directory}")
                self.vector_db = Chroma(
                    persist_directory=self.persist_directory,
                    embedding_function=self.embeddings
                )
            
            # Load document sources if available
            sources_path = os.path.join(self.persist_directory, "sources.json")
            if os.path.exists(sources_path):
                with open(sources_path, 'r') as f:
                    self.document_sources = json.load(f)
        except Exception as e:
            print(f"Error initializing vector database: {e}")
            # Fallback to in-memory database
            print("Falling back to in-memory database")
            self.vector_db = Chroma(embedding_function=self.embeddings)
    
    def _save_document_sources(self):
        """Save document sources to disk."""
        try:
            sources_path = os.path.join(self.persist_directory, "sources.json")
            with open(sources_path, 'w') as f:
                json.dump(self.document_sources, f, indent=2)
        except Exception as e:
            print(f"Error saving document sources: {e}")
    
    def load_document(self, file_path: str, metadata: Dict = None) -> List[Document]:
        """
        Load a document based on its file extension.
        
        Args:
            file_path: Path to the document
            metadata: Additional metadata to attach to the document
            
        Returns:
            List of Document objects
        """
        if not metadata:
            metadata = {"source": file_path}
        
        file_ext = os.path.splitext(file_path)[1].lower()
        
        try:
            if file_ext == '.txt':
                loader = TextLoader(file_path)
            elif file_ext == '.pdf':
                loader = PyPDFLoader(file_path)
            elif file_ext in ['.docx', '.doc']:
                loader = Docx2txtLoader(file_path)
            else:
                raise ValueError(f"Unsupported file type: {file_ext}")
            
            documents = loader.load()
            
            # Add metadata to each document
            for doc in documents:
                doc.metadata.update(metadata)
            
            return documents
            
        except Exception as e:
            print(f"Error loading document {file_path}: {e}")
            return []
    
    def add_documents(self, 
                     file_paths: List[str], 
                     document_type: str,
                     owner_id: str,
                     client_id: Optional[str] = None):
        """
        Add multiple documents to the knowledge base.
        
        Args:
            file_paths: List of paths to documents
            document_type: Type of document (specialist_reference, client_reference)
            owner_id: ID of the document owner
            client_id: Optional client ID for client-specific documents
        """
        all_docs = []
        
        for file_path in file_paths:
            metadata = {
                "document_type": document_type,
                "owner_id": owner_id,
                "client_id": client_id if client_id else "",
                "source": file_path
            }
            
            # Load document
            documents = self.load_document(file_path, metadata)
            
            if not documents:
                print(f"No content extracted from {file_path}")
                continue
            
            # Split documents into chunks
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=1000,
                chunk_overlap=200
            )
            split_docs = text_splitter.split_documents(documents)
            print(f"Split {file_path} into {len(split_docs)} chunks")
            all_docs.extend(split_docs)
            
            # Track source documents
            doc_id = f"{document_type}_{owner_id}_{os.path.basename(file_path)}"
            self.document_sources[doc_id] = {
                "path": file_path,
                "type": document_type,
                "owner": owner_id,
                "client": client_id if client_id else "",
                "chunks": len(split_docs)
            }
        
        # Add to vector store
        if all_docs:
            print(f"Adding {len(all_docs)} document chunks to vector database")
            self.vector_db.add_documents(all_docs)
            self.vector_db.persist()
            self._save_document_sources()
        else:
            print("No documents to add")
    
    def search(self, 
              query: str, 
              filter_criteria: Optional[Dict] = None,
              top_k: int = 5) -> List[Dict]:
        """
        Search for relevant content based on query and filters.
        
        Args:
            query: The search query
            filter_criteria: Optional filters like document_type, owner_id, client_id
            top_k: Number of results to return
            
        Returns:
            List of documents with content and metadata
        """
        if not self.vector_db:
            return []
        
        # Clean empty values from filter criteria
        if filter_criteria:
            filter_criteria = {k: v for k, v in filter_criteria.items() if v}
        
        try:
            # Use the similarity_search_with_relevance_scores method to get scores
            results = self.vector_db.similarity_search_with_relevance_scores(
                query, 
                k=top_k,
                filter=filter_criteria
            )
            
            return [{
                "content": doc.page_content,
                "metadata": doc.metadata,
                "score": float(score)  # Convert np.float32 to float for JSON serialization
            } for doc, score in results]
        
        except Exception as e:
            print(f"Error searching vector database: {e}")
            return []
    
    def analyze_writing_style(self, specialist_id: str) -> Dict[str, Any]:
        """
        Analyze a specialist's writing style based on their documents.
        
        Args:
            specialist_id: ID of the specialist
            
        Returns:
            Dictionary with writing style characteristics
        """
        # Check cache first
        cache_key = f"style_analysis_{specialist_id}"
        cached_result = self.cache.get(cache_key)
        if cached_result:
            print(f"Using cached style analysis for {specialist_id}")
            return cached_result
        
        # Get specialist documents
        filter_criteria = {
            "document_type": "specialist_reference",
            "owner_id": specialist_id
        }
        
        documents = self.search(
            query="writing style tone voice structure",
            filter_criteria=filter_criteria,
            top_k=10
        )
        
        if not documents:
            print(f"No documents found for specialist {specialist_id}")
            return {}
        
        # Use LLM to analyze writing style
        llm = initialize_llm(model_name="gpt-4o", temperature=0.2)
        
        # Select most relevant content samples
        content_samples = "\n\n---\n\n".join(
            [f"SAMPLE {i+1}:\n{doc['content']}" for i, doc in enumerate(documents[:5])]
        )
        
        prompt = f"""
        Analyze the following text samples from a content writer and describe their writing style.
        Focus on:
        - Tone (formal, casual, technical, etc.)
        - Sentence structure (simple, complex, varied)
        - Vocabulary level (basic, intermediate, advanced)
        - Paragraph organization (logical flow, structure)
        - Voice (active vs passive)
        - Use of rhetorical devices
        - Any distinctive patterns or preferences
        
        Text samples:
        {content_samples}
        
        Provide your analysis as a valid JSON object with the following structure:
        {{
            "tone": "description of the tone",
            "sentence_structure": "description of sentence structure",
            "vocabulary_level": "description of vocabulary level",
            "paragraph_structure": "description of paragraph organization",
            "voice": "description of voice preference",
            "rhetorical_devices": "description of rhetorical devices used",
            "distinctive_patterns": "description of any distinctive patterns",
            "overall_style": "summary of overall writing style"
        }}
        
        Return ONLY the JSON object, nothing else.
        """
        
        try:
            response = llm.invoke(prompt)
            
            # Parse JSON response
            import json
            style_analysis = json.loads(response.content)
            
            # Cache the result
            self.cache.set(cache_key, style_analysis)
            
            return style_analysis
        
        except json.JSONDecodeError:
            print(f"Error parsing JSON from LLM response for {specialist_id}")
            # Attempt to extract JSON from the response
            import re
            json_match = re.search(r'({[\s\S]*})', response.content)
            if json_match:
                try:
                    style_analysis = json.loads(json_match.group(1))
                    self.cache.set(cache_key, style_analysis)
                    return style_analysis
                except:
                    pass
            
            # Fallback to simplified analysis
            fallback = {
                "tone": "unknown",
                "sentence_structure": "unknown",
                "vocabulary_level": "unknown",
                "paragraph_structure": "unknown",
                "voice": "unknown",
                "rhetorical_devices": "unknown",
                "distinctive_patterns": "unknown",
                "overall_style": response.content
            }
            self.cache.set(cache_key, fallback)
            return fallback
        
        except Exception as e:
            print(f"Error analyzing writing style for {specialist_id}: {e}")
            return {
                "tone": "unknown",
                "sentence_structure": "unknown",
                "vocabulary_level": "unknown",
                "paragraph_structure": "unknown",
                "voice": "unknown",
                "rhetorical_devices": "unknown",
                "distinctive_patterns": "unknown",
                "overall_style": "Could not analyze writing style"
            }
    
    def analyze_client_content(self, client_id: str) -> Dict[str, Any]:
        """
        Analyze a client's existing content for patterns and preferences.
        
        Args:
            client_id: ID of the client
            
        Returns:
            Dictionary with content patterns and preferences
        """
        # Check cache first
        cache_key = f"client_analysis_{client_id}"
        cached_result = self.cache.get(cache_key)
        if cached_result:
            print(f"Using cached client analysis for {client_id}")
            return cached_result
        
        # Get client-specific documents
        filter_criteria = {
            "document_type": "client_reference",
            "client_id": client_id
        }
        
        documents = self.search(
            query="content style preferences terminology audience",
            filter_criteria=filter_criteria,
            top_k=10
        )
        
        if not documents:
            print(f"No documents found for client {client_id}")
            return {}
        
        # Use LLM to analyze client preferences
        llm = initialize_llm(model_name="gpt-4o", temperature=0.2)
        
        # Select most relevant content samples
        content_samples = "\n\n---\n\n".join(
            [f"SAMPLE {i+1}:\n{doc['content']}" for i, doc in enumerate(documents[:5])]
        )
        
        prompt = f"""
        Analyze the following content samples from a client and identify their preferences and patterns.
        Focus on:
        - Industry-specific terminology and phrases
        - Tone and voice preferences
        - Content structure preferences
        - Target audience characteristics
        - Key messaging themes
        - Taboo topics or terms they avoid
        - Competitors mentioned
        
        Content samples:
        {content_samples}
        
        Provide your analysis as a valid JSON object with the following structure:
        {{
            "industry_terms": ["term1", "term2", ...],
            "tone": "description of preferred tone",
            "structure_preferences": "description of content structure preferences",
            "target_audience": ["audience1", "audience2", ...],
            "key_themes": ["theme1", "theme2", ...],
            "taboo_topics": ["topic/term1", "topic/term2", ...],
            "competitors": ["competitor1", "competitor2", ...],
            "overall_analysis": "summary of client content preferences"
        }}
        
        Return ONLY the JSON object, nothing else.
        """
        
        try:
            response = llm.invoke(prompt)
            
            # Parse JSON response
            import json
            client_analysis = json.loads(response.content)
            
            # Cache the result
            self.cache.set(cache_key, client_analysis)
            
            return client_analysis
        
        except json.JSONDecodeError:
            print(f"Error parsing JSON from LLM response for {client_id}")
            # Attempt to extract JSON from the response
            import re
            json_match = re.search(r'({[\s\S]*})', response.content)
            if json_match:
                try:
                    client_analysis = json.loads(json_match.group(1))
                    self.cache.set(cache_key, client_analysis)
                    return client_analysis
                except:
                    pass
            
            # Fallback if JSON parsing fails
            fallback = {
                "industry_terms": [],
                "tone": "unknown",
                "structure_preferences": "unknown",
                "target_audience": [],
                "key_themes": [],
                "taboo_topics": [],
                "competitors": [],
                "overall_analysis": response.content
            }
            self.cache.set(cache_key, fallback)
            return fallback
        
        except Exception as e:
            print(f"Error analyzing client content for {client_id}: {e}")
            return {
                "industry_terms": [],
                "tone": "unknown",
                "structure_preferences": "unknown",
                "target_audience": [],
                "key_themes": [],
                "taboo_topics": [],
                "competitors": [],
                "overall_analysis": "Could not analyze client content"
            }
    
    def clear_documents(self, 
                       document_type: Optional[str] = None,
                       owner_id: Optional[str] = None,
                       client_id: Optional[str] = None) -> int:
        """
        Clear documents from the knowledge base based on filters.
        
        Args:
            document_type: Optional document type to filter
            owner_id: Optional owner ID to filter
            client_id: Optional client ID to filter
            
        Returns:
            Number of documents cleared
        """
        if not self.vector_db:
            return 0
        
        filter_criteria = {}
        if document_type:
            filter_criteria["document_type"] = document_type
        if owner_id:
            filter_criteria["owner_id"] = owner_id
        if client_id:
            filter_criteria["client_id"] = client_id
        
        try:
            # Count documents before deletion
            ids_to_delete = self.vector_db._collection.get(
                where=filter_criteria,
                include=["documents"]
            )
            
            # Delete documents
            self.vector_db._collection.delete(
                where=filter_criteria
            )
            
            # Update document sources
            new_sources = {}
            for doc_id, source in self.document_sources.items():
                keep = True
                if document_type and source["type"] == document_type:
                    keep = False
                if owner_id and source["owner"] == owner_id:
                    keep = False
                if client_id and source["client"] == client_id:
                    keep = False
                
                if keep:
                    new_sources[doc_id] = source
            
            self.document_sources = new_sources
            self._save_document_sources()
            
            return len(ids_to_delete["ids"])
        
        except Exception as e:
            print(f"Error clearing documents: {e}")
            return 0