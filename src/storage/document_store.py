import os
import json
import pickle
import numpy as np
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
import logging
from dataclasses import dataclass, asdict
import faiss
from ..embeddings.embedding_generator import LocalEmbeddingGenerator

@dataclass
class Document:
    """Document class with metadata and content."""
    id: str
    content: str
    metadata: Dict[str, Any]
    embedding: Optional[np.ndarray] = None
    created_at: datetime = None
    updated_at: datetime = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.updated_at is None:
            self.updated_at = datetime.now()

class DocumentStore:
    """
    Document storage and retrieval system using FAISS for efficient similarity search.
    """
    
    def __init__(self, store_path: str = "data/documents", 
                 embedding_dim: int = 384,
                 embedding_generator: Optional[LocalEmbeddingGenerator] = None):
        """
        Initialize the document store.
        
        Args:
            store_path: Path to store documents and indexes
            embedding_dim: Dimension of embeddings
            embedding_generator: Embedding generator instance
        """
        self.store_path = store_path
        self.embedding_dim = embedding_dim
        self.embedding_generator = embedding_generator
        
        # Create directories
        os.makedirs(store_path, exist_ok=True)
        os.makedirs(os.path.join(store_path, "indexes"), exist_ok=True)
        
        # Initialize FAISS index
        self.index = None
        self.documents = {}
        self.doc_id_to_index = {}
        
        # Load existing data if available
        self._load_data()
    
    def _load_data(self):
        """Load existing documents and index from disk."""
        try:
            # Load documents
            docs_file = os.path.join(self.store_path, "documents.json")
            if os.path.exists(docs_file):
                with open(docs_file, 'r', encoding='utf-8') as f:
                    docs_data = json.load(f)
                    
                for doc_data in docs_data:
                    doc = Document(**doc_data)
                    # Convert string embedding back to numpy array
                    if doc.embedding and isinstance(doc.embedding, list):
                        doc.embedding = np.array(doc.embedding)
                    self.documents[doc.id] = doc
                
                logging.info(f"Loaded {len(self.documents)} documents")
            
            # Load FAISS index
            index_file = os.path.join(self.store_path, "indexes", "faiss.index")
            if os.path.exists(index_file):
                self.index = faiss.read_index(index_file)
                
                # Rebuild doc_id_to_index mapping
                for i, doc_id in enumerate(self.documents.keys()):
                    self.doc_id_to_index[doc_id] = i
                
                logging.info(f"Loaded FAISS index with {self.index.ntotal} vectors")
            else:
                # Initialize new index
                self.index = faiss.IndexFlatIP(self.embedding_dim)  # Inner product for cosine similarity
                
        except Exception as e:
            logging.error(f"Error loading data: {e}")
            # Initialize empty structures
            self.documents = {}
            self.doc_id_to_index = {}
            self.index = faiss.IndexFlatIP(self.embedding_dim)
    
    def _save_data(self):
        """Save documents and index to disk."""
        try:
            # Save documents
            docs_file = os.path.join(self.store_path, "documents.json")
            docs_data = []
            for doc in self.documents.values():
                doc_dict = asdict(doc)
                # Convert numpy array to list for JSON serialization
                if doc_dict['embedding'] is not None:
                    doc_dict['embedding'] = doc_dict['embedding'].tolist()
                docs_data.append(doc_dict)
            
            with open(docs_file, 'w', encoding='utf-8') as f:
                json.dump(docs_data, f, indent=2, default=str)
            
            # Save FAISS index
            index_file = os.path.join(self.store_path, "indexes", "faiss.index")
            faiss.write_index(self.index, index_file)
            
            logging.info("Data saved successfully")
        except Exception as e:
            logging.error(f"Error saving data: {e}")
    
    def add_document(self, content: str, metadata: Optional[Dict[str, Any]] = None, 
                    doc_id: Optional[str] = None) -> str:
        """
        Add a document to the store.
        
        Args:
            content: Document content
            metadata: Document metadata
            doc_id: Optional document ID (auto-generated if not provided)
            
        Returns:
            Document ID
        """
        if doc_id is None:
            doc_id = f"doc_{len(self.documents)}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        if metadata is None:
            metadata = {}
        
        # Create document
        doc = Document(id=doc_id, content=content, metadata=metadata)
        
        # Generate embedding if generator is available
        if self.embedding_generator:
            doc.embedding = self.embedding_generator.generate_embedding(content)
        
        # Add to documents
        self.documents[doc_id] = doc
        
        # Add to FAISS index if embedding is available
        if doc.embedding is not None:
            # Normalize embedding for cosine similarity
            normalized_embedding = doc.embedding / np.linalg.norm(doc.embedding)
            self.index.add(normalized_embedding.reshape(1, -1))
            self.doc_id_to_index[doc_id] = self.index.ntotal - 1
        
        # Save data
        self._save_data()
        
        logging.info(f"Added document {doc_id}")
        return doc_id
    
    def add_documents_batch(self, documents: List[Dict[str, Any]]) -> List[str]:
        """
        Add multiple documents to the store.
        
        Args:
            documents: List of document dictionaries with 'content' and optional 'metadata'
            
        Returns:
            List of document IDs
        """
        doc_ids = []
        
        for i, doc_data in enumerate(documents):
            content = doc_data.get('content', '')
            metadata = doc_data.get('metadata', {})
            doc_id = doc_data.get('id', f"doc_{len(self.documents)}_{i}_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
            
            doc_ids.append(self.add_document(content, metadata, doc_id))
        
        return doc_ids
    
    def get_document(self, doc_id: str) -> Optional[Document]:
        """
        Get a document by ID.
        
        Args:
            doc_id: Document ID
            
        Returns:
            Document or None if not found
        """
        return self.documents.get(doc_id)
    
    def update_document(self, doc_id: str, content: Optional[str] = None, 
                       metadata: Optional[Dict[str, Any]] = None) -> bool:
        """
        Update a document.
        
        Args:
            doc_id: Document ID
            content: New content (optional)
            metadata: New metadata (optional)
            
        Returns:
            True if successful, False otherwise
        """
        doc = self.documents.get(doc_id)
        if not doc:
            return False
        
        # Update content and regenerate embedding
        if content is not None:
            doc.content = content
            if self.embedding_generator:
                doc.embedding = self.embedding_generator.generate_embedding(content)
        
        # Update metadata
        if metadata is not None:
            doc.metadata.update(metadata)
        
        doc.updated_at = datetime.now()
        
        # Update FAISS index
        if doc.embedding is not None and doc_id in self.doc_id_to_index:
            # Normalize embedding
            normalized_embedding = doc.embedding / np.linalg.norm(doc.embedding)
            index_pos = self.doc_id_to_index[doc_id]
            self.index.remove_ids(np.array([index_pos]))
            self.index.add(normalized_embedding.reshape(1, -1))
            self.doc_id_to_index[doc_id] = self.index.ntotal - 1
        
        # Save data
        self._save_data()
        
        logging.info(f"Updated document {doc_id}")
        return True
    
    def delete_document(self, doc_id: str) -> bool:
        """
        Delete a document from the store.
        
        Args:
            doc_id: Document ID
            
        Returns:
            True if successful, False otherwise
        """
        if doc_id not in self.documents:
            return False
        
        # Remove from FAISS index
        if doc_id in self.doc_id_to_index:
            index_pos = self.doc_id_to_index[doc_id]
            self.index.remove_ids(np.array([index_pos]))
            del self.doc_id_to_index[doc_id]
        
        # Remove from documents
        del self.documents[doc_id]
        
        # Save data
        self._save_data()
        
        logging.info(f"Deleted document {doc_id}")
        return True
    
    def search_similar(self, query: str, top_k: int = 5, 
                      similarity_threshold: float = 0.0) -> List[Tuple[Document, float]]:
        """
        Search for similar documents.
        
        Args:
            query: Query text
            top_k: Number of results to return
            similarity_threshold: Minimum similarity score
            
        Returns:
            List of (Document, similarity_score) tuples
        """
        if not self.embedding_generator or self.index.ntotal == 0:
            return []
        
        try:
            # Generate query embedding
            query_embedding = self.embedding_generator.generate_embedding(query)
            
            # Normalize query embedding
            query_embedding = query_embedding / np.linalg.norm(query_embedding)
            
            # Search in FAISS index
            scores, indices = self.index.search(query_embedding.reshape(1, -1), min(top_k, self.index.ntotal))
            
            results = []
            for score, idx in zip(scores[0], indices[0]):
                if score >= similarity_threshold:
                    # Find document by index
                    doc_id = None
                    for did, di in self.doc_id_to_index.items():
                        if di == idx:
                            doc_id = did
                            break
                    
                    if doc_id and doc_id in self.documents:
                        doc = self.documents[doc_id]
                        results.append((doc, float(score)))
            
            return results
        except Exception as e:
            logging.error(f"Error searching similar documents: {e}")
            return []
    
    def search_by_metadata(self, metadata_filter: Dict[str, Any], 
                          top_k: Optional[int] = None) -> List[Document]:
        """
        Search documents by metadata.
        
        Args:
            metadata_filter: Dictionary of metadata key-value pairs to match
            top_k: Maximum number of results (optional)
            
        Returns:
            List of matching documents
        """
        results = []
        
        for doc in self.documents.values():
            match = True
            for key, value in metadata_filter.items():
                if key not in doc.metadata or doc.metadata[key] != value:
                    match = False
                    break
            
            if match:
                results.append(doc)
        
        # Sort by creation date (newest first)
        results.sort(key=lambda x: x.created_at, reverse=True)
        
        if top_k is not None:
            results = results[:top_k]
        
        return results
    
    def get_all_documents(self) -> List[Document]:
        """Get all documents in the store."""
        return list(self.documents.values())
    
    def get_document_count(self) -> int:
        """Get the number of documents in the store."""
        return len(self.documents)
    
    def clear_store(self):
        """Clear all documents from the store."""
        self.documents.clear()
        self.doc_id_to_index.clear()
        self.index = faiss.IndexFlatIP(self.embedding_dim)
        self._save_data()
        logging.info("Document store cleared")
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get statistics about the document store."""
        return {
            'total_documents': len(self.documents),
            'indexed_documents': len(self.doc_id_to_index),
            'embedding_dimension': self.embedding_dim,
            'store_path': self.store_path,
            'has_embedding_generator': self.embedding_generator is not None
        }
