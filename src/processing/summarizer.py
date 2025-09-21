import logging
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
import re
from collections import Counter
import numpy as np

@dataclass
class Summary:
    """Represents a summary of document(s)."""
    content: str
    key_points: List[str]
    source_documents: List[str]
    summary_type: str
    confidence_score: float
    metadata: Dict[str, Any]

class DocumentSummarizer:
    """
    Summarization system for multiple documents and research results.
    """
    
    def __init__(self, max_sentences: int = 5, min_sentence_length: int = 10):
        """
        Initialize the summarizer.
        
        Args:
            max_sentences: Maximum number of sentences in summary
            min_sentence_length: Minimum length of sentences to consider
        """
        self.max_sentences = max_sentences
        self.min_sentence_length = min_sentence_length
        
        logging.info(f"DocumentSummarizer initialized with max_sentences={max_sentences}")
    
    def summarize_documents(self, documents: List[Dict[str, Any]], 
                           summary_type: str = "extractive") -> Summary:
        """
        Summarize multiple documents into a coherent research report.
        
        Args:
            documents: List of document dictionaries with 'content' and 'metadata'
            summary_type: Type of summarization ('extractive', 'abstractive', 'hybrid')
            
        Returns:
            Summary object
        """
        if not documents:
            return Summary(
                content="No documents to summarize.",
                key_points=[],
                source_documents=[],
                summary_type=summary_type,
                confidence_score=0.0,
                metadata={"error": "No documents provided"}
            )
        
        try:
            # Extract content from documents
            contents = [doc.get('content', '') for doc in documents]
            source_docs = [doc.get('id', 'unknown') for doc in documents]
            
            if summary_type == "extractive":
                return self._extractive_summary(contents, source_docs)
            elif summary_type == "abstractive":
                return self._abstractive_summary(contents, source_docs)
            elif summary_type == "hybrid":
                return self._hybrid_summary(contents, source_docs)
            else:
                raise ValueError(f"Unknown summary type: {summary_type}")
                
        except Exception as e:
            logging.error(f"Error summarizing documents: {e}")
            return Summary(
                content=f"Error generating summary: {str(e)}",
                key_points=[],
                source_documents=[],
                summary_type=summary_type,
                confidence_score=0.0,
                metadata={"error": str(e)}
            )
    
    def summarize_query_results(self, query_result: Dict[str, Any]) -> Summary:
        """
        Summarize query results into a research report.
        
        Args:
            query_result: Query result dictionary
            
        Returns:
            Summary object
        """
        try:
            # Extract information from query result
            query = query_result.get('query', '')
            answer = query_result.get('answer', '')
            retrieved_docs = query_result.get('retrieved_documents', [])
            reasoning_steps = query_result.get('reasoning_steps', [])
            confidence = query_result.get('confidence_score', 0.0)
            
            # Create summary content
            summary_content = self._create_query_summary(
                query, answer, retrieved_docs, reasoning_steps
            )
            
            # Extract key points
            key_points = self._extract_key_points_from_results(
                query_result, retrieved_docs, reasoning_steps
            )
            
            # Get source document IDs
            source_docs = [doc.get('id', 'unknown') for doc in retrieved_docs]
            
            return Summary(
                content=summary_content,
                key_points=key_points,
                source_documents=source_docs,
                summary_type="query_result",
                confidence_score=confidence,
                metadata={
                    "query": query,
                    "retrieved_count": len(retrieved_docs),
                    "reasoning_steps_count": len(reasoning_steps)
                }
            )
            
        except Exception as e:
            logging.error(f"Error summarizing query results: {e}")
            return Summary(
                content=f"Error generating summary: {str(e)}",
                key_points=[],
                source_documents=[],
                summary_type="query_result",
                confidence_score=0.0,
                metadata={"error": str(e)}
            )
    
    def _extractive_summary(self, contents: List[str], source_docs: List[str]) -> Summary:
        """Generate extractive summary by selecting important sentences."""
        # Combine all content
        combined_content = ' '.join(contents)
        
        # Split into sentences
        sentences = self._split_into_sentences(combined_content)
        
        # Filter sentences by length
        sentences = [s for s in sentences if len(s.split()) >= self.min_sentence_length]
        
        if not sentences:
            return Summary(
                content="No suitable sentences found for summarization.",
                key_points=[],
                source_documents=source_docs,
                summary_type="extractive",
                confidence_score=0.0,
                metadata={"sentence_count": 0}
            )
        
        # Score sentences based on importance
        sentence_scores = self._score_sentences(sentences)
        
        # Select top sentences
        top_sentences = self._select_top_sentences(sentences, sentence_scores)
        
        # Generate summary
        summary_content = ' '.join(top_sentences)
        
        # Extract key points
        key_points = self._extract_key_points(top_sentences)
        
        # Calculate confidence
        confidence = min(len(sentences) / 10.0, 1.0)  # More sentences = higher confidence
        
        return Summary(
            content=summary_content,
            key_points=key_points,
            source_documents=source_docs,
            summary_type="extractive",
            confidence_score=confidence,
            metadata={
                "total_sentences": len(sentences),
                "summary_sentences": len(top_sentences),
                "average_sentence_score": np.mean(sentence_scores) if sentence_scores else 0.0
            }
        )
    
    def _abstractive_summary(self, contents: List[str], source_docs: List[str]) -> Summary:
        """Generate abstractive summary (simplified version)."""
        # For now, we'll use a simplified approach since we don't have access to
        # large language models for true abstractive summarization
        
        # Combine content and extract key information
        combined_content = ' '.join(contents)
        
        # Extract key concepts and themes
        key_concepts = self._extract_key_concepts(combined_content)
        
        # Generate abstractive summary based on key concepts
        summary_content = self._generate_abstractive_content(key_concepts, combined_content)
        
        # Create key points
        key_points = [f"Key concept: {concept}" for concept in key_concepts[:5]]
        
        return Summary(
            content=summary_content,
            key_points=key_points,
            source_documents=source_docs,
            summary_type="abstractive",
            confidence_score=0.7,  # Moderate confidence for abstractive
            metadata={
                "key_concepts_count": len(key_concepts),
                "abstractive_method": "simplified"
            }
        )
    
    def _hybrid_summary(self, contents: List[str], source_docs: List[str]) -> Summary:
        """Generate hybrid summary combining extractive and abstractive approaches."""
        # First, generate extractive summary
        extractive_summary = self._extractive_summary(contents, source_docs)
        
        # Then, enhance it with abstractive elements
        enhanced_content = self._enhance_summary_abstractive(
            extractive_summary.content, 
            extractive_summary.key_points
        )
        
        # Combine key points
        key_points = extractive_summary.key_points[:3]  # Top extractive points
        key_points.extend([f"Analysis: {point}" for point in extractive_summary.key_points[3:6]])  # Analysis points
        
        return Summary(
            content=enhanced_content,
            key_points=key_points,
            source_documents=source_docs,
            summary_type="hybrid",
            confidence_score=0.8,  # Higher confidence for hybrid
            metadata={
                "extractive_sentences": len(extractive_summary.content.split('.')),
                "abstractive_enhancement": True,
                "original_confidence": extractive_summary.confidence_score
            }
        )
    
    def _create_query_summary(self, query: str, answer: str, 
                            retrieved_docs: List[Dict], 
                            reasoning_steps: List[Dict]) -> str:
        """Create a comprehensive summary of query results."""
        summary_parts = []
        
        # Query context
        summary_parts.append(f"Research Query: {query}")
        summary_parts.append("")
        
        # Main answer
        summary_parts.append("Research Findings:")
        summary_parts.append(answer)
        summary_parts.append("")
        
        # Source information
        if retrieved_docs:
            summary_parts.append(f"Sources Consulted: {len(retrieved_docs)} documents")
            for i, doc in enumerate(retrieved_docs[:3]):  # Top 3 sources
                summary_parts.append(f"  {i+1}. Document {doc.get('id', 'unknown')}")
            summary_parts.append("")
        
        # Reasoning process
        if reasoning_steps:
            summary_parts.append("Research Methodology:")
            for step in reasoning_steps:
                step_type = step.get('step_type', 'unknown')
                description = step.get('description', 'No description')
                summary_parts.append(f"  • {step_type}: {description}")
            summary_parts.append("")
        
        # Confidence assessment
        confidence = reasoning_steps[-1].get('confidence', 0.0) if reasoning_steps else 0.0
        confidence_level = "High" if confidence > 0.7 else "Medium" if confidence > 0.4 else "Low"
        summary_parts.append(f"Confidence Level: {confidence_level}")
        
        return '\n'.join(summary_parts)
    
    def _extract_key_points_from_results(self, query_result: Dict, 
                                       retrieved_docs: List[Dict], 
                                       reasoning_steps: List[Dict]) -> List[str]:
        """Extract key points from query results."""
        key_points = []
        
        # Add query as context
        query = query_result.get('query', '')
        if query:
            key_points.append(f"Research Question: {query}")
        
        # Extract from retrieved documents
        for doc in retrieved_docs[:3]:  # Top 3 documents
            content = doc.get('content', '')
            if content:
                # Get first sentence as key point
                sentences = self._split_into_sentences(content)
                if sentences:
                    key_points.append(f"Source Finding: {sentences[0]}")
        
        # Extract from reasoning steps
        for step in reasoning_steps:
            step_type = step.get('step_type', '')
            if step_type in ['fact_extraction', 'logical_deduction', 'synthesis']:
                description = step.get('description', '')
                if description:
                    key_points.append(f"Analysis Step: {description}")
        
        return key_points[:10]  # Limit to 10 key points
    
    # Helper methods
    def _split_into_sentences(self, text: str) -> List[str]:
        """Split text into sentences."""
        # Simple sentence splitting - can be improved with NLP libraries
        sentences = re.split(r'[.!?]+', text)
        return [s.strip() for s in sentences if s.strip()]
    
    def _score_sentences(self, sentences: List[str]) -> List[float]:
        """Score sentences based on importance."""
        scores = []
        
        # Simple scoring based on:
        # 1. Sentence length (longer sentences might be more important)
        # 2. Position (sentences at beginning and end might be more important)
        # 3. Keyword frequency
        
        # Get word frequencies
        all_words = ' '.join(sentences).lower().split()
        word_freq = Counter(all_words)
        
        for i, sentence in enumerate(sentences):
            score = 0.0
            
            # Length score
            word_count = len(sentence.split())
            length_score = min(word_count / 20.0, 1.0)  # Normalize to 0-1
            score += length_score * 0.3
            
            # Position score
            position_score = 1.0 if i < 2 or i >= len(sentences) - 2 else 0.5
            score += position_score * 0.3
            
            # Keyword frequency score
            sentence_words = sentence.lower().split()
            if sentence_words:
                avg_freq = np.mean([word_freq.get(word, 0) for word in sentence_words])
                freq_score = min(avg_freq / 2.0, 1.0)  # Normalize
                score += freq_score * 0.4
            
            scores.append(score)
        
        return scores
    
    def _select_top_sentences(self, sentences: List[str], scores: List[float]) -> List[str]:
        """Select top sentences based on scores."""
        # Pair sentences with scores
        sentence_score_pairs = list(zip(sentences, scores))
        
        # Sort by score (descending)
        sentence_score_pairs.sort(key=lambda x: x[1], reverse=True)
        
        # Select top sentences
        top_sentences = [pair[0] for pair in sentence_score_pairs[:self.max_sentences]]
        
        # Maintain original order for readability
        original_order_sentences = []
        for sentence in sentences:
            if sentence in top_sentences and sentence not in original_order_sentences:
                original_order_sentences.append(sentence)
                if len(original_order_sentences) >= self.max_sentences:
                    break
        
        return original_order_sentences
    
    def _extract_key_points(self, sentences: List[str]) -> List[str]:
        """Extract key points from sentences."""
        key_points = []
        
        for sentence in sentences:
            # Look for sentences that contain key indicators
            sentence_lower = sentence.lower()
            
            # Check for important patterns
            important_patterns = [
                r'\b(important|key|main|primary|essential|critical|significant)\b',
                r'\b(conclusion|finding|result|discovery|observation)\b',
                r'\b(therefore|thus|consequently|as a result)\b',
                r'\b(first|second|finally|overall|in summary)\b'
            ]
            
            for pattern in important_patterns:
                if re.search(pattern, sentence_lower):
                    key_points.append(sentence)
                    break
        
        # If no important patterns found, use the first few sentences
        if not key_points:
            key_points = sentences[:3]
        
        return key_points
    
    def _extract_key_concepts(self, text: str) -> List[str]:
        """Extract key concepts from text."""
        # Simple concept extraction based on noun phrases and important terms
        words = text.lower().split()
        
        # Filter out common stop words
        stop_words = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 
            'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'have', 'has', 'had',
            'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might', 'can',
            'this', 'that', 'these', 'those', 'there', 'here', 'when', 'where', 'how', 'why'
        }
        
        # Get word frequencies
        word_freq = Counter(words)
        
        # Filter out stop words and short words
        concepts = [
            word for word, freq in word_freq.items() 
            if word not in stop_words and len(word) > 3 and freq >= 2
        ]
        
        # Sort by frequency
        concepts.sort(key=lambda x: word_freq[x], reverse=True)
        
        return concepts[:10]  # Top 10 concepts
    
    def _generate_abstractive_content(self, key_concepts: List[str], original_content: str) -> str:
        """Generate abstractive summary content."""
        if not key_concepts:
            return "No key concepts identified for abstractive summary."
        
        # Create a structured summary based on key concepts
        summary_parts = []
        
        summary_parts.append("This document discusses several important concepts and themes.")
        summary_parts.append("")
        
        # Add key concepts
        summary_parts.append("Key themes include:")
        for i, concept in enumerate(key_concepts[:5], 1):
            summary_parts.append(f"  {i}. {concept.title()}")
        
        summary_parts.append("")
        summary_parts.append("The content explores these topics in detail, providing insights and analysis on the subject matter.")
        summary_parts.append("Further examination reveals the interconnected nature of these concepts and their significance.")
        
        return '\n'.join(summary_parts)
    
    def _enhance_summary_abstractive(self, extractive_content: str, key_points: List[str]) -> str:
        """Enhance extractive summary with abstractive elements."""
        enhanced_parts = []
        
        # Add abstractive introduction
        enhanced_parts.append("This research summary provides a comprehensive overview of the key findings and insights.")
        enhanced_parts.append("")
        
        # Add extractive content
        enhanced_parts.append(extractive_content)
        enhanced_parts.append("")
        
        # Add abstractive conclusion
        enhanced_parts.append("In conclusion, the research highlights important patterns and relationships within the subject matter.")
        enhanced_parts.append("These findings contribute to a deeper understanding of the topic and suggest areas for further investigation.")
        
        return '\n'.join(enhanced_parts)
    
    def compare_summaries(self, summaries: List[Summary]) -> Dict[str, Any]:
        """
        Compare multiple summaries.
        
        Args:
            summaries: List of Summary objects
            
        Returns:
            Comparison dictionary
        """
        if not summaries:
            return {"error": "No summaries to compare"}
        
        comparison = {
            "summary_count": len(summaries),
            "types": [s.summary_type for s in summaries],
            "average_confidence": np.mean([s.confidence_score for s in summaries]),
            "content_lengths": [len(s.content) for s in summaries],
            "key_points_counts": [len(s.key_points) for s in summaries],
            "source_overlap": self._calculate_source_overlap(summaries)
        }
        
        return comparison
    
    def _calculate_source_overlap(self, summaries: List[Summary]) -> Dict[str, Any]:
        """Calculate overlap between source documents of summaries."""
        all_sources = set()
        for summary in summaries:
            all_sources.update(summary.source_documents)
        
        overlap_matrix = []
        for i, summary1 in enumerate(summaries):
            row = []
            for j, summary2 in enumerate(summaries):
                if i == j:
                    row.append(1.0)
                else:
                    set1 = set(summary1.source_documents)
                    set2 = set(summary2.source_documents)
                    if len(set1.union(set2)) == 0:
                        row.append(0.0)
                    else:
                        overlap = len(set1.intersection(set2)) / len(set1.union(set2))
                        row.append(overlap)
            overlap_matrix.append(row)
        
        return {
            "total_unique_sources": len(all_sources),
            "overlap_matrix": overlap_matrix
        }
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about the document summarizer.
        
        Returns:
            Dictionary containing summarizer statistics
        """
        try:
            stats = {
                "max_sentences": self.max_sentences,
                "min_sentence_length": self.min_sentence_length,
                "supported_summary_types": ["extractive", "abstractive", "hybrid"],
                "status": "active",
                "capabilities": {
                    "multi_document": True,
                    "key_point_extraction": True,
                    "confidence_scoring": True,
                    "metadata_preservation": True
                },
                "performance_metrics": {
                    "average_summary_length": 0,
                    "total_summaries_generated": 0,
                    "average_confidence_score": 0.0
                }
            }
            
            return stats
            
        except Exception as e:
            logging.error(f"Error getting summarizer statistics: {e}")
            return {
                "error": str(e),
                "status": "error"
            }
