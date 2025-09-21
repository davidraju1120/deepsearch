import logging
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
import json

from ..embeddings.embedding_generator import LocalEmbeddingGenerator, EmbeddingManager
from ..storage.document_store import DocumentStore
from ..reasoning.reasoning_engine import ReasoningEngine, ReasoningPlan

@dataclass
class QueryResult:
    """Result of a query execution."""
    query: str
    answer: str
    confidence_score: float
    reasoning_steps: List[Dict[str, Any]]
    retrieved_documents: List[Dict[str, Any]]
    execution_time: float
    metadata: Dict[str, Any]
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "query": self.query,
            "answer": self.answer,
            "confidence_score": self.confidence_score,
            "reasoning_steps": self.reasoning_steps,
            "retrieved_documents": self.retrieved_documents,
            "execution_time": self.execution_time,
            "metadata": self.metadata,
            "timestamp": self.timestamp.isoformat()
        }

class QueryHandler:
    """
    Main query handling system that orchestrates the entire research process.
    """
    
    def __init__(self, 
                 document_store_path: str = "data/documents",
                 embedding_model: str = "all-MiniLM-L6-v2",
                 enable_reasoning: bool = True):
        """
        Initialize the query handler.
        
        Args:
            document_store_path: Path to document store
            embedding_model: Name of embedding model to use
            enable_reasoning: Whether to enable multi-step reasoning
        """
        self.document_store_path = document_store_path
        self.embedding_model = embedding_model
        self.enable_reasoning = enable_reasoning
        
        # Initialize components
        self.embedding_manager = EmbeddingManager()
        self.embedding_generator = self.embedding_manager.load_model(embedding_model)
        self.document_store = DocumentStore(
            store_path=document_store_path,
            embedding_dim=self.embedding_generator.embedding_dim,
            embedding_generator=self.embedding_generator
        )
        self.reasoning_engine = ReasoningEngine(self.document_store) if enable_reasoning else None
        
        # Query history
        self.query_history = []
        
        logging.info(f"QueryHandler initialized with model: {embedding_model}")
    
    def process_query(self, query: str, 
                     search_params: Optional[Dict[str, Any]] = None,
                     reasoning_params: Optional[Dict[str, Any]] = None) -> QueryResult:
        """
        Process a query and return results.
        
        Args:
            query: The query to process
            search_params: Parameters for document search
            reasoning_params: Parameters for reasoning engine
            
        Returns:
            QueryResult object
        """
        start_time = datetime.now()
        
        try:
            # Set default parameters
            search_params = search_params or {}
            reasoning_params = reasoning_params or {}
            
            logging.info(f"Processing query: {query}")
            
            # Process query based on whether reasoning is enabled
            if self.enable_reasoning and self.reasoning_engine:
                result = self._process_query_with_reasoning(query, search_params, reasoning_params)
            else:
                result = self._process_query_simple(query, search_params)
            
            # Calculate execution time
            execution_time = (datetime.now() - start_time).total_seconds()
            result.execution_time = execution_time
            
            # Add to history
            self.query_history.append(result)
            
            logging.info(f"Query processed successfully in {execution_time:.2f} seconds")
            return result
            
        except Exception as e:
            logging.error(f"Error processing query: {e}")
            # Return error result
            return QueryResult(
                query=query,
                answer=f"Error processing query: {str(e)}",
                confidence_score=0.0,
                reasoning_steps=[],
                retrieved_documents=[],
                execution_time=0.0,
                metadata={"error": str(e)}
            )
    
    def _process_query_simple(self, query: str, search_params: Dict[str, Any]) -> QueryResult:
        """Process query using simple document retrieval."""
        # Search for similar documents
        top_k = search_params.get("top_k", 5)
        similarity_threshold = search_params.get("similarity_threshold", 0.0)
        
        retrieved_docs = self.document_store.search_similar(
            query, 
            top_k=top_k, 
            similarity_threshold=similarity_threshold
        )
        
        # Generate simple answer
        answer = self._generate_simple_answer(query, retrieved_docs)
        
        # Calculate confidence
        confidence = self._calculate_simple_confidence(retrieved_docs)
        
        # Format retrieved documents
        formatted_docs = [
            {
                "id": doc.id,
                "content": doc.content,
                "metadata": doc.metadata,
                "similarity_score": score
            }
            for doc, score in retrieved_docs
        ]
        
        return QueryResult(
            query=query,
            answer=answer,
            confidence_score=confidence,
            reasoning_steps=[],
            retrieved_documents=formatted_docs,
            execution_time=0.0,
            metadata={"processing_mode": "simple"}
        )
    
    def _process_query_with_reasoning(self, query: str, 
                                   search_params: Dict[str, Any],
                                   reasoning_params: Dict[str, Any]) -> QueryResult:
        """Process query using multi-step reasoning."""
        # Create reasoning plan
        plan = self.reasoning_engine.create_reasoning_plan(query)
        
        # Execute reasoning plan
        executed_plan = self.reasoning_engine.execute_reasoning_plan(plan)
        
        # Extract information from the executed plan
        answer = executed_plan.final_answer or "No answer generated"
        confidence_score = executed_plan.confidence_score or 0.0
        
        # Format reasoning steps
        reasoning_steps = []
        for step in executed_plan.steps:
            reasoning_steps.append({
                "step_id": step.step_id,
                "step_type": step.step_type.value,
                "description": step.description,
                "confidence": step.confidence,
                "dependencies": step.dependencies,
                "output_summary": self._summarize_step_output(step.output_data)
            })
        
        # Extract retrieved documents from reasoning steps
        retrieved_docs = []
        for step in executed_plan.steps:
            if step.step_type.value == "information_retrieval":
                retrieved_docs = step.output_data.get("retrieved_documents", [])
                break
        
        return QueryResult(
            query=query,
            answer=answer,
            confidence_score=confidence_score,
            reasoning_steps=reasoning_steps,
            retrieved_documents=retrieved_docs,
            execution_time=0.0,
            metadata={"processing_mode": "reasoning", "reasoning_params": reasoning_params}
        )
    
    def _generate_simple_answer(self, query: str, retrieved_docs: List[Tuple[Any, float]]) -> str:
        """Generate a simple answer from retrieved documents."""
        if not retrieved_docs:
            return "No relevant documents were found to answer your query."
        
        # Use the top document to generate answer
        top_doc, top_score = retrieved_docs[0]
        
        answer = f"Based on the most relevant document found (similarity: {top_score:.3f}):\n\n"
        answer += top_doc.content
        
        if len(retrieved_docs) > 1:
            answer += f"\n\nFound {len(retrieved_docs)} relevant documents in total."
        
        return answer
    
    def _calculate_simple_confidence(self, retrieved_docs: List[Tuple[Any, float]]) -> float:
        """Calculate confidence score for simple query processing."""
        if not retrieved_docs:
            return 0.0
        
        # Use average similarity score as confidence
        avg_similarity = sum(score for _, score in retrieved_docs) / len(retrieved_docs)
        
        # Adjust based on number of documents
        doc_count_factor = min(len(retrieved_docs) / 5.0, 1.0)
        
        return avg_similarity * doc_count_factor
    
    def _summarize_step_output(self, output_data: Dict[str, Any]) -> str:
        """Summarize step output for display."""
        if not output_data:
            return "No output"
        
        if "error" in output_data:
            return f"Error: {output_data['error']}"
        
        # Create a summary based on output type
        summary_parts = []
        
        if "retrieved_documents" in output_data:
            count = len(output_data["retrieved_documents"])
            summary_parts.append(f"Retrieved {count} documents")
        
        if "extracted_facts" in output_data:
            count = len(output_data["extracted_facts"])
            summary_parts.append(f"Extracted {count} facts")
        
        if "logical_deductions" in output_data:
            count = len(output_data["logical_deductions"])
            summary_parts.append(f"Made {count} deductions")
        
        if "key_points" in output_data:
            count = len(output_data["key_points"])
            summary_parts.append(f"Identified {count} key points")
        
        if "answer_summary" in output_data:
            summary_parts.append("Generated answer summary")
        
        return "; ".join(summary_parts) if summary_parts else "Processing completed"
    
    def process_batch_queries(self, queries: List[str], 
                            search_params: Optional[Dict[str, Any]] = None,
                            reasoning_params: Optional[Dict[str, Any]] = None) -> List[QueryResult]:
        """
        Process multiple queries in batch.
        
        Args:
            queries: List of queries to process
            search_params: Parameters for document search
            reasoning_params: Parameters for reasoning engine
            
        Returns:
            List of QueryResult objects
        """
        results = []
        
        for i, query in enumerate(queries):
            logging.info(f"Processing batch query {i+1}/{len(queries)}: {query}")
            
            try:
                result = self.process_query(query, search_params, reasoning_params)
                results.append(result)
            except Exception as e:
                logging.error(f"Error processing batch query {i+1}: {e}")
                # Add error result
                results.append(QueryResult(
                    query=query,
                    answer=f"Error processing query: {str(e)}",
                    confidence_score=0.0,
                    reasoning_steps=[],
                    retrieved_documents=[],
                    execution_time=0.0,
                    metadata={"error": str(e)}
                ))
        
        return results
    
    def get_query_suggestions(self, partial_query: str, max_suggestions: int = 5) -> List[str]:
        """
        Get query suggestions based on partial input.
        
        Args:
            partial_query: Partial query text
            max_suggestions: Maximum number of suggestions
            
        Returns:
            List of suggested query completions
        """
        # This is a simple implementation - in a real system, you might use
        # more sophisticated methods like analyzing query history or document content
        
        suggestions = []
        
        # Get all documents and extract key terms
        all_docs = self.document_store.get_all_documents()
        
        # Simple keyword-based suggestions
        keywords = set()
        for doc in all_docs:
            words = doc.content.lower().split()
            for word in words:
                if len(word) > 3 and word.startswith(partial_query.lower()):
                    keywords.add(word)
        
        # Convert to suggestions
        for keyword in sorted(keywords)[:max_suggestions]:
            suggestions.append(f"{partial_query} {keyword}")
        
        return suggestions
    
    def refine_query(self, original_query: str, feedback: str) -> str:
        """
        Refine a query based on user feedback.
        
        Args:
            original_query: Original query
            feedback: User feedback on the result
            
        Returns:
            Refined query
        """
        # Simple query refinement based on feedback
        feedback_lower = feedback.lower()
        
        # Add specificity based on feedback
        if "more specific" in feedback_lower or "detailed" in feedback_lower:
            return f"{original_query} detailed explanation"
        
        if "examples" in feedback_lower:
            return f"{original_query} with examples"
        
        if "compare" in feedback_lower:
            return f"compare {original_query}"
        
        if "causes" in feedback_lower or "why" in feedback_lower:
            return f"why {original_query}"
        
        if "how to" in feedback_lower:
            return f"how to {original_query}"
        
        # Default refinement - add context
        return f"{original_query} comprehensive analysis"
    
    def get_query_statistics(self) -> Dict[str, Any]:
        """Get statistics about query processing."""
        if not self.query_history:
            return {"total_queries": 0}
        
        total_queries = len(self.query_history)
        avg_execution_time = sum(q.execution_time for q in self.query_history) / total_queries
        avg_confidence = sum(q.confidence_score for q in self.query_history) / total_queries
        
        reasoning_queries = sum(1 for q in self.query_history if q.metadata.get("processing_mode") == "reasoning")
        
        return {
            "total_queries": total_queries,
            "average_execution_time": avg_execution_time,
            "average_confidence_score": avg_confidence,
            "reasoning_queries": reasoning_queries,
            "simple_queries": total_queries - reasoning_queries,
            "document_store_stats": self.document_store.get_statistics()
        }
    
    def get_query_history(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Get query history.
        
        Args:
            limit: Maximum number of queries to return
            
        Returns:
            List of query results as dictionaries
        """
        history = [q.to_dict() for q in self.query_history]
        
        if limit:
            history = history[-limit:]
        
        return history
    
    def clear_query_history(self):
        """Clear the query history."""
        self.query_history.clear()
        logging.info("Query history cleared")
    
    def export_query_results(self, output_path: str, format_type: str = "json"):
        """
        Export query results to file.
        
        Args:
            output_path: Path to output file
            format_type: Export format ('json' or 'csv')
        """
        if not self.query_history:
            logging.warning("No query results to export")
            return
        
        try:
            if format_type.lower() == "json":
                with open(output_path, 'w', encoding='utf-8') as f:
                    json.dump([q.to_dict() for q in self.query_history], f, indent=2, default=str)
            
            elif format_type.lower() == "csv":
                import csv
                
                with open(output_path, 'w', newline='', encoding='utf-8') as f:
                    if self.query_history:
                        writer = csv.DictWriter(f, fieldnames=self.query_history[0].to_dict().keys())
                        writer.writeheader()
                        for result in self.query_history:
                            writer.writerow(result.to_dict())
            
            logging.info(f"Query results exported to {output_path}")
            
        except Exception as e:
            logging.error(f"Error exporting query results: {e}")
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get system status information."""
        return {
            "embedding_model": self.embedding_model,
            "embedding_model_info": self.embedding_generator.get_model_info(),
            "document_store_stats": self.document_store.get_statistics(),
            "reasoning_enabled": self.enable_reasoning,
            "query_stats": self.get_query_statistics(),
            "system_ready": True
        }
