import logging
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
import json
import re

from ..reasoning.reasoning_engine import ReasoningEngine, ReasoningPlan, ReasoningStepType
from ..storage.document_store import DocumentStore
from ..embeddings.embedding_generator import LocalEmbeddingGenerator

@dataclass
class RefinementQuestion:
    """Question for query refinement."""
    question_id: str
    question_text: str
    question_type: str  # 'clarification', 'scope', 'focus', 'detail'
    options: List[str]
    context: str
    importance: str  # 'high', 'medium', 'low'

@dataclass
class RefinementResponse:
    """Response to a refinement question."""
    question_id: str
    response: str
    confidence: float
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()

@dataclass
class RefinementSession:
    """A query refinement session."""
    session_id: str
    original_query: str
    current_query: str
    questions: List[RefinementQuestion]
    responses: List[RefinementResponse]
    refinement_count: int
    max_refinements: int
    confidence_threshold: float
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()

class QueryRefiner:
    """
    Interactive query refinement system that helps users refine their queries
    through follow-up questions and suggestions.
    """
    
    def __init__(self, document_store: DocumentStore, embedding_generator: LocalEmbeddingGenerator,
                 reasoning_engine: ReasoningEngine, max_refinements: int = 3, 
                 confidence_threshold: float = 0.6):
        """
        Initialize the query refiner.
        
        Args:
            document_store: Document store for context
            embedding_generator: Embedding generator for similarity
            reasoning_engine: Reasoning engine for analysis
            max_refinements: Maximum number of refinement rounds
            confidence_threshold: Confidence threshold for stopping refinement
        """
        self.document_store = document_store
        self.embedding_generator = embedding_generator
        self.reasoning_engine = reasoning_engine
        self.max_refinements = max_refinements
        self.confidence_threshold = confidence_threshold
        self.refinement_sessions = {}
        
        # Question templates
        self.question_templates = self._load_question_templates()
        
        logging.info("QueryRefiner initialized")
    
    def start_refinement_session(self, query: str) -> RefinementSession:
        """
        Start a new refinement session for a query.
        
        Args:
            query: Original query to refine
            
        Returns:
            RefinementSession object
        """
        try:
            session_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            # Analyze the initial query
            query_analysis = self._analyze_query(query)
            
            # Generate refinement questions
            questions = self._generate_refinement_questions(query, query_analysis)
            
            # Create session
            session = RefinementSession(
                session_id=session_id,
                original_query=query,
                current_query=query,
                questions=questions,
                responses=[],
                refinement_count=0,
                max_refinements=self.max_refinements,
                confidence_threshold=self.confidence_threshold
            )
            
            self.refinement_sessions[session_id] = session
            logging.info(f"Started refinement session {session_id} for query: {query}")
            
            return session
            
        except Exception as e:
            logging.error(f"Error starting refinement session: {e}")
            raise
    
    def process_response(self, session_id: str, question_id: str, response: str, 
                        confidence: float = 1.0) -> RefinementSession:
        """
        Process a user response to a refinement question.
        
        Args:
            session_id: Session identifier
            question_id: Question identifier
            response: User response
            confidence: Response confidence (0-1)
            
        Returns:
            Updated RefinementSession
        """
        try:
            session = self.refinement_sessions.get(session_id)
            if not session:
                raise ValueError(f"Session {session_id} not found")
            
            # Create response
            refinement_response = RefinementResponse(
                question_id=question_id,
                response=response,
                confidence=confidence
            )
            
            session.responses.append(refinement_response)
            
            # Refine the query based on the response
            refined_query = self._refine_query(session, question_id, response)
            session.current_query = refined_query
            session.refinement_count += 1
            
            # Check if we need more questions
            if session.refinement_count < session.max_refinements:
                # Analyze the refined query
                query_analysis = self._analyze_query(refined_query)
                
                # Generate new questions if needed
                new_questions = self._generate_refinement_questions(refined_query, query_analysis)
                if new_questions:
                    session.questions.extend(new_questions)
            
            logging.info(f"Processed response for session {session_id}, refined query: {refined_query}")
            return session
            
        except Exception as e:
            logging.error(f"Error processing response: {e}")
            raise
    
    def should_continue_refinement(self, session_id: str) -> bool:
        """
        Check if refinement should continue for a session.
        
        Args:
            session_id: Session identifier
            
        Returns:
            True if refinement should continue, False otherwise
        """
        try:
            session = self.refinement_sessions.get(session_id)
            if not session:
                return False
            
            # Check if we've reached max refinements
            if session.refinement_count >= session.max_refinements:
                return False
            
            # Check if current query has high confidence
            query_confidence = self._assess_query_confidence(session.current_query)
            if query_confidence >= session.confidence_threshold:
                return False
            
            # Check if there are unanswered questions
            unanswered_questions = self._get_unanswered_questions(session)
            if not unanswered_questions:
                return False
            
            return True
            
        except Exception as e:
            logging.error(f"Error checking refinement continuation: {e}")
            return False
    
    def get_refinement_suggestions(self, session_id: str) -> List[str]:
        """
        Get suggestions for query refinement.
        
        Args:
            session_id: Session identifier
            
        Returns:
            List of suggestion strings
        """
        try:
            session = self.refinement_sessions.get(session_id)
            if not session:
                return []
            
            suggestions = []
            
            # Analyze current query
            query_analysis = self._analyze_query(session.current_query)
            
            # Generate suggestions based on analysis
            if query_analysis.get("is_vague", False):
                suggestions.append("Consider adding more specific keywords or context")
            
            if query_analysis.get("is_broad", False):
                suggestions.append("Consider narrowing the scope to a specific aspect")
            
            if query_analysis.get("lacks_context", False):
                suggestions.append("Consider providing more background information")
            
            if query_analysis.get("ambiguous_terms", []):
                ambiguous_terms = query_analysis["ambiguous_terms"]
                suggestions.append(f"Clarify ambiguous terms: {', '.join(ambiguous_terms)}")
            
            # Add domain-specific suggestions
            domain_suggestions = self._get_domain_suggestions(session.current_query)
            suggestions.extend(domain_suggestions)
            
            return suggestions
            
        except Exception as e:
            logging.error(f"Error getting refinement suggestions: {e}")
            return []
    
    def get_refinement_summary(self, session_id: str) -> Dict[str, Any]:
        """
        Get a summary of the refinement session.
        
        Args:
            session_id: Session identifier
            
        Returns:
            Refinement summary dictionary
        """
        try:
            session = self.refinement_sessions.get(session_id)
            if not session:
                return {}
            
            summary = {
                "session_id": session_id,
                "original_query": session.original_query,
                "final_query": session.current_query,
                "refinement_count": session.refinement_count,
                "questions_asked": len(session.questions),
                "responses_received": len(session.responses),
                "improvement_score": self._calculate_improvement_score(session),
                "confidence_progression": self._calculate_confidence_progression(session),
                "key_changes": self._identify_key_changes(session),
                "timestamp": session.timestamp.isoformat()
            }
            
            return summary
            
        except Exception as e:
            logging.error(f"Error getting refinement summary: {e}")
            return {}
    
    def auto_refine_query(self, query: str) -> Tuple[str, Dict[str, Any]]:
        """
        Automatically refine a query without user interaction.
        
        Args:
            query: Original query
            
        Returns:
            Tuple of (refined_query, refinement_info)
        """
        try:
            refinement_info = {
                "original_query": query,
                "refinements_applied": [],
                "confidence_improvement": 0.0,
                "changes_made": []
            }
            
            current_query = query
            original_confidence = self._assess_query_confidence(query)
            
            # Apply automatic refinements
            refinements = self._get_auto_refinements(query)
            
            for refinement in refinements:
                if self._should_apply_refinement(current_query, refinement):
                    refined_query = self._apply_refinement(current_query, refinement)
                    new_confidence = self._assess_query_confidence(refined_query)
                    
                    if new_confidence > original_confidence:
                        current_query = refined_query
                        refinement_info["refinements_applied"].append(refinement["type"])
                        refinement_info["changes_made"].append(refinement["description"])
                        refinement_info["confidence_improvement"] = new_confidence - original_confidence
            
            refinement_info["final_confidence"] = self._assess_query_confidence(current_query)
            
            return current_query, refinement_info
            
        except Exception as e:
            logging.error(f"Error in auto refinement: {e}")
            return query, {"error": str(e)}
    
    def _analyze_query(self, query: str) -> Dict[str, Any]:
        """Analyze a query to identify refinement opportunities."""
        try:
            analysis = {
                "query": query,
                "word_count": len(query.split()),
                "is_vague": False,
                "is_broad": False,
                "lacks_context": False,
                "ambiguous_terms": [],
                "key_concepts": [],
                "confidence_score": 0.0
            }
            
            # Check for vague terms
            vague_terms = ["something", "thing", "stuff", "information", "about"]
            if any(term in query.lower() for term in vague_terms):
                analysis["is_vague"] = True
            
            # Check for broad terms
            broad_terms = ["everything", "all", "every", "whole", "complete"]
            if any(term in query.lower() for term in broad_terms):
                analysis["is_broad"] = True
            
            # Check for context
            context_markers = ["in", "during", "about", "regarding", "concerning"]
            if not any(marker in query.lower() for marker in context_markers):
                analysis["lacks_context"] = True
            
            # Identify ambiguous terms
            ambiguous_patterns = [
                r"\b(it|this|that|these|those)\b",
                r"\b(recent|latest|current)\b",
                r"\b(good|bad|important|significant)\b"
            ]
            
            for pattern in ambiguous_patterns:
                matches = re.findall(pattern, query.lower())
                analysis["ambiguous_terms"].extend(matches)
            
            analysis["ambiguous_terms"] = list(set(analysis["ambiguous_terms"]))
            
            # Extract key concepts
            key_concepts = self._extract_key_concepts(query)
            analysis["key_concepts"] = key_concepts
            
            # Calculate confidence score
            analysis["confidence_score"] = self._assess_query_confidence(query)
            
            return analysis
            
        except Exception as e:
            logging.error(f"Error analyzing query: {e}")
            return {"query": query, "error": str(e)}
    
    def _generate_refinement_questions(self, query: str, analysis: Dict[str, Any]) -> List[RefinementQuestion]:
        """Generate refinement questions based on query analysis."""
        questions = []
        
        try:
            # Generate questions based on analysis
            if analysis.get("is_vague", False):
                question = RefinementQuestion(
                    question_id=f"q_{len(questions) + 1}",
                    question_text="Could you be more specific about what you're looking for?",
                    question_type="clarification",
                    options=["I need specific examples", "I need detailed information", "I need an overview", "I need comparisons"],
                    context="The query seems vague and could benefit from more specificity",
                    importance="high"
                )
                questions.append(question)
            
            if analysis.get("is_broad", False):
                question = RefinementQuestion(
                    question_id=f"q_{len(questions) + 1}",
                    question_text="Would you like to focus on a specific aspect or time period?",
                    question_type="scope",
                    options=["Recent developments", "Historical context", "Specific examples", "Theoretical aspects"],
                    context="The query is quite broad and could be narrowed down",
                    importance="medium"
                )
                questions.append(question)
            
            if analysis.get("lacks_context", False):
                question = RefinementQuestion(
                    question_id=f"q_{len(questions) + 1}",
                    question_text="What context or background information would be helpful?",
                    question_type="context",
                    options=["Technical background", "Historical context", "Practical applications", "Theoretical framework"],
                    context="The query lacks context that could help provide more relevant results",
                    importance="medium"
                )
                questions.append(question)
            
            if analysis.get("ambiguous_terms", []):
                ambiguous_terms = analysis["ambiguous_terms"][:3]  # Limit to first 3
                question = RefinementQuestion(
                    question_id=f"q_{len(questions) + 1}",
                    question_text=f"Could you clarify what you mean by: {', '.join(ambiguous_terms)}?",
                    question_type="clarification",
                    options=["Define these terms", "Provide examples", "Specify context", "Remove these terms"],
                    context="The query contains ambiguous terms that need clarification",
                    importance="high"
                )
                questions.append(question)
            
            # Add domain-specific questions
            domain_questions = self._generate_domain_questions(query, analysis)
            questions.extend(domain_questions)
            
            # Limit questions to avoid overwhelming the user
            return questions[:3]
            
        except Exception as e:
            logging.error(f"Error generating refinement questions: {e}")
            return []
    
    def _refine_query(self, session: RefinementSession, question_id: str, response: str) -> str:
        """Refine the query based on user response."""
        try:
            current_query = session.current_query
            
            # Find the question
            question = None
            for q in session.questions:
                if q.question_id == question_id:
                    question = q
                    break
            
            if not question:
                return current_query
            
            # Apply refinement based on question type and response
            if question.question_type == "clarification":
                current_query = self._apply_clarification_refinement(current_query, response)
            elif question.question_type == "scope":
                current_query = self._apply_scope_refinement(current_query, response)
            elif question.question_type == "focus":
                current_query = self._apply_focus_refinement(current_query, response)
            elif question.question_type == "detail":
                current_query = self._apply_detail_refinement(current_query, response)
            elif question.question_type == "context":
                current_query = self._apply_context_refinement(current_query, response)
            
            return current_query
            
        except Exception as e:
            logging.error(f"Error refining query: {e}")
            return session.current_query
    
    def _apply_clarification_refinement(self, query: str, response: str) -> str:
        """Apply clarification refinement to query."""
        # Replace vague terms with more specific ones based on response
        vague_to_specific = {
            "something": response.lower(),
            "thing": response.lower(),
            "information": f"{response.lower()} information",
            "about": f"about {response.lower()}"
        }
        
        refined_query = query
        for vague, specific in vague_to_specific.items():
            if vague in query.lower():
                refined_query = refined_query.lower().replace(vague, specific)
        
        return refined_query
    
    def _apply_scope_refinement(self, query: str, response: str) -> str:
        """Apply scope refinement to query."""
        # Add scope-specific terms
        scope_terms = {
            "recent developments": "recent developments in",
            "historical context": "historical context of",
            "specific examples": "examples of",
            "theoretical aspects": "theoretical aspects of"
        }
        
        for scope, term in scope_terms.items():
            if scope.lower() in response.lower():
                return f"{term} {query}"
        
        return query
    
    def _apply_focus_refinement(self, query: str, response: str) -> str:
        """Apply focus refinement to query."""
        # Add focus-specific terms
        return f"{query} focusing on {response.lower()}"
    
    def _apply_detail_refinement(self, query: str, response: str) -> str:
        """Apply detail refinement to query."""
        # Add detail-specific terms
        detail_terms = {
            "detailed": "detailed",
            "comprehensive": "comprehensive",
            "in-depth": "in-depth",
            "overview": "overview of"
        }
        
        for detail, term in detail_terms.items():
            if detail.lower() in response.lower():
                return f"{term} {query}"
        
        return query
    
    def _apply_context_refinement(self, query: str, response: str) -> str:
        """Apply context refinement to query."""
        # Add context-specific terms
        context_terms = {
            "technical background": "technical background of",
            "historical context": "historical context of",
            "practical applications": "practical applications of",
            "theoretical framework": "theoretical framework of"
        }
        
        for context, term in context_terms.items():
            if context.lower() in response.lower():
                return f"{term} {query}"
        
        return query
    
    def _assess_query_confidence(self, query: str) -> float:
        """Assess the confidence score of a query."""
        try:
            confidence = 0.5  # Base confidence
            
            # Increase confidence for specific queries
            if len(query.split()) > 5:
                confidence += 0.1
            
            # Increase confidence for queries with specific terms
            specific_terms = ["how", "what", "why", "when", "where", "who", "which"]
            if any(term in query.lower() for term in specific_terms):
                confidence += 0.1
            
            # Decrease confidence for vague queries
            vague_terms = ["something", "thing", "stuff", "information", "about"]
            if any(term in query.lower() for term in vague_terms):
                confidence -= 0.2
            
            # Decrease confidence for ambiguous queries
            ambiguous_terms = ["it", "this", "that", "recent", "latest"]
            if any(term in query.lower() for term in ambiguous_terms):
                confidence -= 0.1
            
            # Ensure confidence is between 0 and 1
            return max(0.0, min(1.0, confidence))
            
        except Exception as e:
            logging.error(f"Error assessing query confidence: {e}")
            return 0.5
    
    def _get_unanswered_questions(self, session: RefinementSession) -> List[RefinementQuestion]:
        """Get unanswered questions for a session."""
        answered_question_ids = {r.question_id for r in session.responses}
        return [q for q in session.questions if q.question_id not in answered_question_ids]
    
    def _extract_key_concepts(self, query: str) -> List[str]:
        """Extract key concepts from a query."""
        try:
            # Simple keyword extraction
            words = query.lower().split()
            stop_words = {"the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for", "of", "with", "by", "is", "are", "was", "were", "be", "been", "being", "have", "has", "had", "do", "does", "did", "will", "would", "could", "should", "may", "might", "must", "can", "this", "that", "these", "those"}
            
            key_concepts = [word for word in words if word not in stop_words and len(word) > 2]
            
            # Remove duplicates and limit to top 5
            return list(set(key_concepts))[:5]
            
        except Exception as e:
            logging.error(f"Error extracting key concepts: {e}")
            return []
    
    def _get_domain_suggestions(self, query: str) -> List[str]:
        """Get domain-specific suggestions for query refinement."""
        suggestions = []
        
        try:
            # Check for technical terms
            technical_terms = ["algorithm", "model", "system", "framework", "architecture", "protocol"]
            if any(term in query.lower() for term in technical_terms):
                suggestions.append("Consider specifying the technical domain or field")
            
            # Check for temporal terms
            temporal_terms = ["history", "development", "evolution", "future", "trends"]
            if any(term in query.lower() for term in temporal_terms):
                suggestions.append("Consider specifying a time period or timeframe")
            
            # Check for comparative terms
            comparative_terms = ["compare", "comparison", "versus", "vs", "difference", "similarities"]
            if any(term in query.lower() for term in comparative_terms):
                suggestions.append("Consider specifying what aspects to compare")
            
            return suggestions
            
        except Exception as e:
            logging.error(f"Error getting domain suggestions: {e}")
            return []
    
    def _generate_domain_questions(self, query: str, analysis: Dict[str, Any]) -> List[RefinementQuestion]:
        """Generate domain-specific refinement questions."""
        questions = []
        
        try:
            # Technical domain questions
            technical_terms = ["algorithm", "model", "system", "framework", "architecture", "protocol"]
            if any(term in query.lower() for term in technical_terms):
                question = RefinementQuestion(
                    question_id=f"q_tech_{len(questions) + 1}",
                    question_text="What specific technical domain or field are you interested in?",
                    question_type="focus",
                    options=["Computer Science", "Data Science", "Engineering", "Mathematics", "Other"],
                    context="The query contains technical terms that could benefit from domain specification",
                    importance="medium"
                )
                questions.append(question)
            
            # Temporal domain questions
            temporal_terms = ["history", "development", "evolution", "future", "trends"]
            if any(term in query.lower() for term in temporal_terms):
                question = RefinementQuestion(
                    question_id=f"q_temp_{len(questions) + 1}",
                    question_text="What time period or timeframe are you interested in?",
                    question_type="scope",
                    options=["Recent (last 5 years)", "Modern (last 20 years)", "Historical (pre-2000)", "Future predictions", "All time periods"],
                    context="The query contains temporal terms that could benefit from time specification",
                    importance="medium"
                )
                questions.append(question)
            
            return questions
            
        except Exception as e:
            logging.error(f"Error generating domain questions: {e}")
            return []
    
    def _calculate_improvement_score(self, session: RefinementSession) -> float:
        """Calculate the improvement score for a refinement session."""
        try:
            original_confidence = self._assess_query_confidence(session.original_query)
            final_confidence = self._assess_query_confidence(session.current_query)
            
            improvement = final_confidence - original_confidence
            return max(0.0, improvement)
            
        except Exception as e:
            logging.error(f"Error calculating improvement score: {e}")
            return 0.0
    
    def _calculate_confidence_progression(self, session: RefinementSession) -> List[float]:
        """Calculate confidence progression throughout refinement session."""
        try:
            progression = []
            
            # Start with original query confidence
            original_confidence = self._assess_query_confidence(session.original_query)
            progression.append(original_confidence)
            
            # Simulate confidence after each response
            current_query = session.original_query
            for response in session.responses:
                # Find the question
                question = None
                for q in session.questions:
                    if q.question_id == response.question_id:
                        question = q
                        break
                
                if question:
                    # Apply refinement
                    if question.question_type == "clarification":
                        current_query = self._apply_clarification_refinement(current_query, response.response)
                    elif question.question_type == "scope":
                        current_query = self._apply_scope_refinement(current_query, response.response)
                    elif question.question_type == "focus":
                        current_query = self._apply_focus_refinement(current_query, response.response)
                    elif question.question_type == "detail":
                        current_query = self._apply_detail_refinement(current_query, response.response)
                    elif question.question_type == "context":
                        current_query = self._apply_context_refinement(current_query, response.response)
                    
                    # Calculate new confidence
                    new_confidence = self._assess_query_confidence(current_query)
                    progression.append(new_confidence)
            
            return progression
            
        except Exception as e:
            logging.error(f"Error calculating confidence progression: {e}")
            return []
    
    def _identify_key_changes(self, session: RefinementSession) -> List[str]:
        """Identify key changes made during refinement."""
        try:
            changes = []
            
            # Compare original and final queries
            original_words = set(session.original_query.lower().split())
            final_words = set(session.current_query.lower().split())
            
            # Identify added words
            added_words = final_words - original_words
            if added_words:
                changes.append(f"Added terms: {', '.join(list(added_words)[:5])}")
            
            # Identify removed words
            removed_words = original_words - final_words
            if removed_words:
                changes.append(f"Removed terms: {', '.join(list(removed_words)[:5])}")
            
            # Check for specific refinement types based on responses
            for response in session.responses:
                question = None
                for q in session.questions:
                    if q.question_id == response.question_id:
                        question = q
                        break
                
                if question:
                    if question.question_type == "clarification":
                        changes.append("Clarified vague terms")
                    elif question.question_type == "scope":
                        changes.append("Narrowed scope")
                    elif question.question_type == "focus":
                        changes.append("Added focus")
                    elif question.question_type == "detail":
                        changes.append("Added detail level")
                    elif question.question_type == "context":
                        changes.append("Added context")
            
            return changes
            
        except Exception as e:
            logging.error(f"Error identifying key changes: {e}")
            return []
    
    def _get_auto_refinements(self, query: str) -> List[Dict[str, Any]]:
        """Get automatic refinements for a query."""
        refinements = []
        
        try:
            # Add context refinement
            if "in" not in query.lower() and "during" not in query.lower():
                refinements.append({
                    "type": "context",
                    "description": "Added context for better understanding",
                    "function": self._apply_context_refinement
                })
            
            # Add specificity refinement
            vague_terms = ["something", "thing", "stuff"]
            if any(term in query.lower() for term in vague_terms):
                refinements.append({
                    "type": "specificity",
                    "description": "Replaced vague terms with specific ones",
                    "function": self._apply_clarification_refinement
                })
            
            # Add detail refinement
            if len(query.split()) < 5:
                refinements.append({
                    "type": "detail",
                    "description": "Added detail level for comprehensive results",
                    "function": self._apply_detail_refinement
                })
            
            return refinements
            
        except Exception as e:
            logging.error(f"Error getting auto refinements: {e}")
            return []
    
    def _should_apply_refinement(self, query: str, refinement: Dict[str, Any]) -> bool:
        """Check if a refinement should be applied."""
        try:
            # Apply refinement and check confidence improvement
            if "function" in refinement:
                refined_query = refinement["function"](query, "detailed")  # Use "detailed" as default
                original_confidence = self._assess_query_confidence(query)
                new_confidence = self._assess_query_confidence(refined_query)
                
                return new_confidence > original_confidence
            
            return False
            
        except Exception as e:
            logging.error(f"Error checking refinement application: {e}")
            return False
    
    def _apply_refinement(self, query: str, refinement: Dict[str, Any]) -> str:
        """Apply a refinement to a query."""
        try:
            if "function" in refinement:
                return refinement["function"](query, "detailed")  # Use "detailed" as default
            
            return query
            
        except Exception as e:
            logging.error(f"Error applying refinement: {e}")
            return query
    
    def _load_question_templates(self) -> Dict[str, Any]:
        """Load question templates for different refinement types."""
        return {
            "clarification": {
                "templates": [
                    "Could you be more specific about {aspect}?",
                    "What do you mean by {term}?",
                    "Could you clarify {aspect}?"
                ]
            },
            "scope": {
                "templates": [
                    "Would you like to focus on a specific {aspect}?",
                    "What {aspect} are you most interested in?",
                    "Should we narrow down to a specific {aspect}?"
                ]
            },
            "focus": {
                "templates": [
                    "What aspect of {topic} should we focus on?",
                    "Which {aspect} is most important to you?",
                    "Should we concentrate on {aspect}?"
                ]
            },
            "detail": {
                "templates": [
                    "What level of detail do you need for {aspect}?",
                    "How detailed should the information about {aspect} be?",
                    "Do you need {aspect} explained in detail?"
                ]
            },
            "context": {
                "templates": [
                    "What context would be helpful for {aspect}?",
                    "Should we consider {aspect} in what context?",
                    "What background about {aspect} would be useful?"
                ]
            }
        }
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about the query refiner.
        
        Returns:
            Dictionary containing refiner statistics
        """
        try:
            stats = {
                "active_sessions": len(self.refinement_sessions),
                "max_refinements": self.max_refinements,
                "confidence_threshold": self.confidence_threshold,
                "session_types": {
                    "clarification": 0,
                    "scope": 0,
                    "focus": 0,
                    "detail": 0,
                    "context": 0
                },
                "total_refinements": 0,
                "average_improvement_score": 0.0,
                "status": "active"
            }
            
            # Calculate session statistics
            for session in self.refinement_sessions.values():
                stats["total_refinements"] += session.refinement_count
                
                # Count question types
                for question in session.questions:
                    if question.question_type in stats["session_types"]:
                        stats["session_types"][question.question_type] += 1
                
                # Calculate improvement score
                improvement_score = self._calculate_improvement_score(session)
                if improvement_score > 0:
                    stats["average_improvement_score"] += improvement_score
            
            # Calculate average improvement
            if len(self.refinement_sessions) > 0:
                stats["average_improvement_score"] /= len(self.refinement_sessions)
            
            return stats
            
        except Exception as e:
            logging.error(f"Error getting refiner statistics: {e}")
            return {
                "error": str(e),
                "status": "error"
            }
