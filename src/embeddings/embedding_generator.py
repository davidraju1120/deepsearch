import os
import numpy as np
from typing import List, Dict, Any, Optional
from sentence_transformers import SentenceTransformer
import torch
import logging
from tqdm import tqdm

class LocalEmbeddingGenerator:
    """
    Local embedding generation using sentence-transformers.
    Supports various pre-trained models for different use cases.
    """
    
    def __init__(self, model_name: str = "all-MiniLM-L6-v2", device: Optional[str] = None):
        """
        Initialize the embedding generator.
        
        Args:
            model_name: Name of the sentence-transformers model to use
            device: Device to run the model on ('cuda', 'cpu', or None for auto-detection)
        """
        self.model_name = model_name
        self.device = device or ('cuda' if torch.cuda.is_available() else 'cpu')
        
        # Initialize the model
        try:
            self.model = SentenceTransformer(model_name, device=self.device)
            self.embedding_dim = self.model.get_sentence_embedding_dimension()
            logging.info(f"Loaded model {model_name} on device {self.device}")
        except Exception as e:
            logging.error(f"Failed to load model {model_name}: {e}")
            raise
        
        # Cache for embeddings to avoid recomputation
        self.embedding_cache = {}
    
    def generate_embedding(self, text: str) -> np.ndarray:
        """
        Generate embedding for a single text.
        
        Args:
            text: Input text to embed
            
        Returns:
            numpy array representing the embedding
        """
        if not text or not text.strip():
            return np.zeros(self.embedding_dim)
        
        # Check cache first
        if text in self.embedding_cache:
            return self.embedding_cache[text]
        
        try:
            # Generate embedding
            embedding = self.model.encode(text, convert_to_numpy=True)
            
            # Cache the result
            self.embedding_cache[text] = embedding
            
            return embedding
        except Exception as e:
            logging.error(f"Error generating embedding for text: {e}")
            return np.zeros(self.embedding_dim)
    
    def generate_embeddings_batch(self, texts: List[str], batch_size: int = 32) -> np.ndarray:
        """
        Generate embeddings for a batch of texts.
        
        Args:
            texts: List of texts to embed
            batch_size: Batch size for processing
            
        Returns:
            numpy array of embeddings
        """
        if not texts:
            return np.array([])
        
        # Filter out empty texts
        valid_texts = [text for text in texts if text and text.strip()]
        if not valid_texts:
            return np.zeros((len(texts), self.embedding_dim))
        
        try:
            # Generate embeddings in batches
            embeddings = self.model.encode(
                valid_texts, 
                batch_size=batch_size, 
                convert_to_numpy=True,
                show_progress_bar=True
            )
            
            # Create result array with proper dimensions
            result = np.zeros((len(texts), self.embedding_dim))
            
            # Map embeddings back to original positions
            valid_idx = 0
            for i, text in enumerate(texts):
                if text and text.strip():
                    result[i] = embeddings[valid_idx]
                    valid_idx += 1
            
            return result
        except Exception as e:
            logging.error(f"Error generating batch embeddings: {e}")
            return np.zeros((len(texts), self.embedding_dim))
    
    def generate_document_embeddings(self, documents: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Generate embeddings for documents with metadata.
        
        Args:
            documents: List of documents with 'content' and 'metadata' keys
            
        Returns:
            List of documents with added 'embedding' key
        """
        if not documents:
            return []
        
        # Extract texts for batch processing
        texts = [doc.get('content', '') for doc in documents]
        
        # Generate embeddings
        embeddings = self.generate_embeddings_batch(texts)
        
        # Add embeddings to documents
        for i, doc in enumerate(documents):
            doc['embedding'] = embeddings[i]
            doc['embedding_model'] = self.model_name
        
        return documents
    
    def compute_similarity(self, embedding1: np.ndarray, embedding2: np.ndarray) -> float:
        """
        Compute cosine similarity between two embeddings.
        
        Args:
            embedding1: First embedding
            embedding2: Second embedding
            
        Returns:
            Cosine similarity score
        """
        try:
            # Normalize embeddings
            norm1 = np.linalg.norm(embedding1)
            norm2 = np.linalg.norm(embedding2)
            
            if norm1 == 0 or norm2 == 0:
                return 0.0
            
            # Compute cosine similarity
            similarity = np.dot(embedding1, embedding2) / (norm1 * norm2)
            return float(similarity)
        except Exception as e:
            logging.error(f"Error computing similarity: {e}")
            return 0.0
    
    def find_similar_embeddings(self, query_embedding: np.ndarray, 
                               candidate_embeddings: np.ndarray, 
                               top_k: int = 5) -> List[tuple]:
        """
        Find most similar embeddings to a query embedding.
        
        Args:
            query_embedding: Query embedding
            candidate_embeddings: Array of candidate embeddings
            top_k: Number of top results to return
            
        Returns:
            List of (index, similarity_score) tuples
        """
        if len(candidate_embeddings) == 0:
            return []
        
        try:
            # Compute similarities
            similarities = []
            for i, candidate_emb in enumerate(candidate_embeddings):
                similarity = self.compute_similarity(query_embedding, candidate_emb)
                similarities.append((i, similarity))
            
            # Sort by similarity (descending)
            similarities.sort(key=lambda x: x[1], reverse=True)
            
            # Return top_k results
            return similarities[:top_k]
        except Exception as e:
            logging.error(f"Error finding similar embeddings: {e}")
            return []
    
    def clear_cache(self):
        """Clear the embedding cache."""
        self.embedding_cache.clear()
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the current model."""
        return {
            'model_name': self.model_name,
            'embedding_dimension': self.embedding_dim,
            'device': self.device,
            'cache_size': len(self.embedding_cache)
        }


class EmbeddingManager:
    """
    Manager class for handling multiple embedding models and caching.
    """
    
    def __init__(self, cache_dir: str = "data/embeddings"):
        """
        Initialize the embedding manager.
        
        Args:
            cache_dir: Directory to store cached embeddings
        """
        self.cache_dir = cache_dir
        self.models = {}
        self.active_model = None
        
        # Create cache directory if it doesn't exist
        os.makedirs(cache_dir, exist_ok=True)
    
    def load_model(self, model_name: str, device: Optional[str] = None) -> LocalEmbeddingGenerator:
        """
        Load an embedding model.
        
        Args:
            model_name: Name of the model to load
            device: Device to run the model on
            
        Returns:
            LocalEmbeddingGenerator instance
        """
        if model_name not in self.models:
            self.models[model_name] = LocalEmbeddingGenerator(model_name, device)
        
        self.active_model = model_name
        return self.models[model_name]
    
    def get_active_model(self) -> Optional[LocalEmbeddingGenerator]:
        """Get the currently active embedding model."""
        if self.active_model and self.active_model in self.models:
            return self.models[self.active_model]
        return None
    
    def list_available_models(self) -> List[str]:
        """List of recommended models for different use cases."""
        return [
            "all-MiniLM-L6-v2",  # Fast, general purpose
            "all-mpnet-base-v2",  # High quality, general purpose
            "multi-qa-mpnet-base-dot-v1",  # Good for QA tasks
            "paraphrase-multilingual-mpnet-base-v2",  # Multilingual
            "sentence-t5-base",  # Good for longer texts
        ]
    
    def save_embeddings(self, embeddings: np.ndarray, filename: str) -> bool:
        """
        Save embeddings to disk.
        
        Args:
            embeddings: Embeddings to save
            filename: Name of the file to save to
            
        Returns:
            True if successful, False otherwise
        """
        try:
            filepath = os.path.join(self.cache_dir, filename)
            np.save(filepath, embeddings)
            return True
        except Exception as e:
            logging.error(f"Error saving embeddings: {e}")
            return False
    
    def load_embeddings(self, filename: str) -> Optional[np.ndarray]:
        """
        Load embeddings from disk.
        
        Args:
            filename: Name of the file to load from
            
        Returns:
            Loaded embeddings or None if failed
        """
        try:
            filepath = os.path.join(self.cache_dir, filename)
            if os.path.exists(filepath):
                return np.load(filepath)
            return None
        except Exception as e:
            logging.error(f"Error loading embeddings: {e}")
            return None
