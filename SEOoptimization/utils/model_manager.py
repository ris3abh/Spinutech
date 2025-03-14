# SEOoptimization/utils/model_manager.py

import os
import torch
from sentence_transformers import SentenceTransformer
from typing import Optional

# Set environment variable to avoid parallelism warnings
os.environ["TOKENIZERS_PARALLELISM"] = "false"

class TransformerModelManager:
    """
    Singleton manager for transformer models to ensure efficient resource usage.
    This class helps prevent repeated loading of the same models
    and provides proper resource management.
    """
    
    _instance = None
    _models = {}
    
    def __new__(cls):
        """Implement singleton pattern."""
        if cls._instance is None:
            cls._instance = super(TransformerModelManager, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        """Initialize the model manager if not already initialized."""
        if not self._initialized:
            self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
            print(f"TransformerModelManager initialized on device: {self.device}")
            self._initialized = True
    
    def get_sentence_transformer(self, model_name: str = 'all-MiniLM-L6-v2') -> SentenceTransformer:
        """
        Get a sentence transformer model by name, loading it if not already loaded.
        
        Args:
            model_name: Name of the sentence-transformers model to load
            
        Returns:
            Loaded SentenceTransformer model
        """
        if model_name not in self._models:
            print(f"Loading sentence transformer model: {model_name}")
            self._models[model_name] = SentenceTransformer(model_name, device=self.device)
        return self._models[model_name]
    
    def encode_text(self, texts, model_name: str = 'all-MiniLM-L6-v2', batch_size: int = 32):
        """
        Encode texts using the specified model with batching for efficiency.
        
        Args:
            texts: List of texts to encode
            model_name: Name of the sentence-transformers model to use
            batch_size: Batch size for encoding
            
        Returns:
            Numpy array of embeddings
        """
        model = self.get_sentence_transformer(model_name)
        return model.encode(texts, batch_size=batch_size)
    
    def clear_model(self, model_name: Optional[str] = None):
        """
        Clear model from memory to free resources.
        
        Args:
            model_name: Name of model to clear, or None to clear all models
        """
        if model_name is None:
            self._models.clear()
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
            print("All models cleared from memory")
        elif model_name in self._models:
            del self._models[model_name]
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
            print(f"Model {model_name} cleared from memory")
    
    def __del__(self):
        """Cleanup resources when the manager is destroyed."""
        self.clear_model()

# Initialize the manager on module import
model_manager = TransformerModelManager()