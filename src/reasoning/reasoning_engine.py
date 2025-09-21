import re
import logging
from typing import List, Dict, Any, Optional, Tuple, Callable
from dataclasses import dataclass, asdict
from datetime import datetime
import json
from enum import Enum

class ReasoningStepType(Enum):
    """Types of reasoning steps."""
    QUERY_ANALYSIS = "query_analysis"
    INFORMATION_RETRIEVAL = "information_retrieval"
    FACT_EXTRACTION = "fact_extraction"
    LOGICAL_DEDUCTION = "logical_deduction"
    HYPOTHESIS_GENERATION = "hypothesis_generation"
    EVIDENCE_EVALUATION = "evidence_evaluation"
    SYNTHESIS = "synthesis"
    CONCLUSION = "conclusion"

@dataclass
class ReasoningStep:
    """A single step in the reasoning process."""
    step_id: str
    step_type: ReasoningStepType
    description: str
    input_data: Dict[str, Any]
    output_data: Dict[str, Any]
    confidence: float
    dependencies: List[str]  # IDs of dependent steps
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()

@dataclass
class ReasoningPlan:
    """A plan for multi-step reasoning."""
    query: str
    steps: List[ReasoningStep]
    final_answer: Optional[str] = None
    confidence_score: Optional[float] = None
    execution_order: List[str] = None
    
    def __post_init__(self):
        if self.execution_order is None:
            self.execution_order = self._determine_execution_order()
    
    def _determine_execution_order(self) -> List[str]:
        """Determine the execution order based on dependencies."""
        if not self.steps:
            return []
        
        # Topological sort
        visited = set()
        temp_visited = set()
        order = []
        
        def visit(step_id: str):
            if step_id in temp_visited:
                raise ValueError(f"Circular dependency detected involving step {step_id}")
            if step_id in visited:
                return
            
            temp_visited.add(step_id)
            
            # Find the step
            step = next((s for s in self.steps if s.step_id == step_id), None)
            if step:
                # Visit dependencies first
                for dep_id in step.dependencies:
                    visit(dep_id)
            
            temp_visited.remove(step_id)
            visited.add(step_id)
            order.append(step_id)
        
        # Visit all steps
        for step in self.steps:
            if step.step_id not in visited:
                visit(step.step_id)
        
        return order

class QueryAnalyzer:
    """Analyzes queries to determine complexity and required reasoning steps."""
    
    def __init__(self):
        self.complexity_keywords = {
            'compare': ['compare', 'contrast', 'difference', 'similarity', 'versus', 'vs'],
            'analyze': ['analyze', 'examine', 'investigate', 'break down', 'explore'],
            'explain': ['explain', 'why', 'how', 'reason', 'cause', 'effect'],
            'synthesize': ['synthesize', 'combine', 'integrate', 'merge', 'summarize'],
            'evaluate': ['evaluate', 'assess', 'judge', 'critique', 'review'],
            'predict': ['predict', 'forecast', 'anticipate', 'expect', 'likely'],
            'recommend': ['recommend', 'suggest', 'advise', 'propose', 'should']
        }
        
        self.question_patterns = {
            'what': r'\bwhat\b',
            'when': r'\bwhen\b',
            'where': r'\bwhere\b',
            'who': r'\bwho\b',
            'why': r'\bwhy\b',
            'how': r'\bhow\b',
            'which': r'\bwhich\b'
        }
    
    def analyze_query(self, query: str) -> Dict[str, Any]:
        """
        Analyze a query to determine its characteristics.
        
        Args:
            query: The query to analyze
            
        Returns:
            Dictionary containing analysis results
        """
        query_lower = query.lower()
        
        analysis = {
            'original_query': query,
            'query_type': self._determine_query_type(query_lower),
            'complexity_level': self._assess_complexity(query_lower),
            'key_concepts': self._extract_key_concepts(query),
            'required_operations': self._identify_required_operations(query_lower),
            'estimated_steps': self._estimate_required_steps(query_lower)
        }
        
        return analysis
    
    def _determine_query_type(self, query: str) -> str:
        """Determine the type of query."""
        for q_type, pattern in self.question_patterns.items():
            if re.search(pattern, query):
                return q_type
        
        # Check for action keywords
        for action, keywords in self.complexity_keywords.items():
            if any(keyword in query for keyword in keywords):
                return action
        
        return 'factual'
    
    def _assess_complexity(self, query: str) -> str:
        """Assess the complexity of the query."""
        complexity_score = 0
        
        # Count action keywords
        for keywords in self.complexity_keywords.values():
            complexity_score += sum(1 for keyword in keywords if keyword in query)
        
        # Check for multiple questions
        question_count = len(re.findall(r'\?', query))
        complexity_score += question_count
        
        # Check for conjunctions indicating multiple aspects
        conjunctions = ['and', 'or', 'but', 'while', 'although']
        complexity_score += sum(1 for conj in conjunctions if conj in query)
        
        # Determine complexity level
        if complexity_score <= 1:
            return 'simple'
        elif complexity_score <= 3:
            return 'moderate'
        else:
            return 'complex'
    
    def _extract_key_concepts(self, query: str) -> List[str]:
        """Extract key concepts from the query."""
        # Simple extraction based on nouns and important terms
        words = re.findall(r'\b\w+\b', query.lower())
        
        # Filter out common stop words
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might', 'can', 'this', 'that', 'these', 'those'}
        
        concepts = [word for word in words if word not in stop_words and len(word) > 2]
        
        # Remove duplicates and return
        return list(set(concepts))
    
    def _identify_required_operations(self, query: str) -> List[str]:
        """Identify required operations for the query."""
        operations = []
        
        for operation, keywords in self.complexity_keywords.items():
            if any(keyword in query for keyword in keywords):
                operations.append(operation)
        
        # Always include retrieval for factual queries
        if not operations:
            operations.append('retrieve')
        
        return operations
    
    def _estimate_required_steps(self, query: str) -> int:
        """Estimate the number of reasoning steps required."""
        complexity = self._assess_complexity(query)
        operations = self._identify_required_operations(query)
        
        base_steps = len(operations)
        
        if complexity == 'simple':
            return max(2, base_steps)
        elif complexity == 'moderate':
            return max(3, base_steps + 1)
        else:  # complex
            return max(4, base_steps + 2)

class ReasoningEngine:
    """
    Multi-step reasoning engine that breaks down complex queries into manageable tasks.
    """
    
    def __init__(self, document_store=None):
        """
        Initialize the reasoning engine.
        
        Args:
            document_store: Document store for information retrieval
        """
        self.document_store = document_store
        self.query_analyzer = QueryAnalyzer()
        self.reasoning_history = []
        self.step_executors = {
            ReasoningStepType.QUERY_ANALYSIS: self._execute_query_analysis,
            ReasoningStepType.INFORMATION_RETRIEVAL: self._execute_information_retrieval,
            ReasoningStepType.FACT_EXTRACTION: self._execute_fact_extraction,
            ReasoningStepType.LOGICAL_DEDUCTION: self._execute_logical_deduction,
            ReasoningStepType.HYPOTHESIS_GENERATION: self._execute_hypothesis_generation,
            ReasoningStepType.EVIDENCE_EVALUATION: self._execute_evidence_evaluation,
            ReasoningStepType.SYNTHESIS: self._execute_synthesis,
            ReasoningStepType.CONCLUSION: self._execute_conclusion
        }
    
    def create_reasoning_plan(self, query: str) -> ReasoningPlan:
        """
        Create a reasoning plan for a given query.
        
        Args:
            query: The query to reason about
            
        Returns:
            ReasoningPlan object
        """
        # Analyze the query
        analysis = self.query_analyzer.analyze_query(query)
        
        # Generate reasoning steps
        steps = self._generate_reasoning_steps(query, analysis)
        
        # Create the plan
        plan = ReasoningPlan(query=query, steps=steps)
        
        logging.info(f"Created reasoning plan with {len(steps)} steps for query: {query}")
        return plan
    
    def _generate_reasoning_steps(self, query: str, analysis: Dict[str, Any]) -> List[ReasoningStep]:
        """Generate reasoning steps based on query analysis."""
        steps = []
        step_counter = 0
        
        # Step 1: Query Analysis
        step_counter += 1
        steps.append(ReasoningStep(
            step_id=f"step_{step_counter}",
            step_type=ReasoningStepType.QUERY_ANALYSIS,
            description="Analyze query to understand requirements",
            input_data={"query": query},
            output_data=analysis,
            confidence=0.9,
            dependencies=[]
        ))
        
        # Step 2: Information Retrieval
        step_counter += 1
        steps.append(ReasoningStep(
            step_id=f"step_{step_counter}",
            step_type=ReasoningStepType.INFORMATION_RETRIEVAL,
            description="Retrieve relevant information from document store",
            input_data={"query": query, "key_concepts": analysis["key_concepts"]},
            output_data={},  # Will be populated during execution
            confidence=0.8,
            dependencies=[f"step_{step_counter-1}"]
        ))
        
        # Additional steps based on complexity
        if analysis["complexity_level"] in ["moderate", "complex"]:
            # Step 3: Fact Extraction
            step_counter += 1
            steps.append(ReasoningStep(
                step_id=f"step_{step_counter}",
                step_type=ReasoningStepType.FACT_EXTRACTION,
                description="Extract key facts from retrieved information",
                input_data={},  # Will depend on retrieval results
                output_data={},
                confidence=0.7,
                dependencies=[f"step_{step_counter-1}"]
            ))
        
        if analysis["complexity_level"] == "complex":
            # Step 4: Logical Deduction
            step_counter += 1
            steps.append(ReasoningStep(
                step_id=f"step_{step_counter}",
                step_type=ReasoningStepType.LOGICAL_DEDUCTION,
                description="Apply logical reasoning to extracted facts",
                input_data={},
                output_data={},
                confidence=0.6,
                dependencies=[f"step_{step_counter-1}"]
            ))
        
        # Final step: Synthesis/Conclusion
        step_counter += 1
        final_step_type = ReasoningStepType.SYNTHESIS if analysis["complexity_level"] == "complex" else ReasoningStepType.CONCLUSION
        steps.append(ReasoningStep(
            step_id=f"step_{step_counter}",
            step_type=final_step_type,
            description="Synthesize information into final answer",
            input_data={},
            output_data={},
            confidence=0.5,
            dependencies=[f"step_{step_counter-1}"]
        ))
        
        return steps
    
    def execute_reasoning_plan(self, plan: ReasoningPlan) -> ReasoningPlan:
        """
        Execute a reasoning plan.
        
        Args:
            plan: The reasoning plan to execute
            
        Returns:
            Updated reasoning plan with execution results
        """
        logging.info(f"Executing reasoning plan for query: {plan.query}")
        
        # Execute steps in order
        for step_id in plan.execution_order:
            step = next((s for s in plan.steps if s.step_id == step_id), None)
            if step:
                try:
                    # Get input data from dependencies
                    input_data = self._gather_input_data(step, plan.steps)
                    step.input_data = input_data
                    
                    # Execute the step
                    executor = self.step_executors.get(step.step_type)
                    if executor:
                        step.output_data = executor(input_data, step)
                        logging.info(f"Executed step {step_id}: {step.description}")
                    else:
                        logging.warning(f"No executor found for step type: {step.step_type}")
                        
                except Exception as e:
                    logging.error(f"Error executing step {step_id}: {e}")
                    step.output_data = {"error": str(e)}
                    step.confidence = 0.0
        
        # Generate final answer
        plan.final_answer = self._generate_final_answer(plan)
        plan.confidence_score = self._calculate_confidence_score(plan)
        
        # Store in history
        self.reasoning_history.append(plan)
        
        return plan
    
    def _gather_input_data(self, step: ReasoningStep, all_steps: List[ReasoningStep]) -> Dict[str, Any]:
        """Gather input data from step dependencies."""
        input_data = step.input_data.copy()
        
        for dep_id in step.dependencies:
            dep_step = next((s for s in all_steps if s.step_id == dep_id), None)
            if dep_step and dep_step.output_data:
                input_data[f"dep_{dep_id}"] = dep_step.output_data
        
        return input_data
    
    def _execute_query_analysis(self, input_data: Dict[str, Any], step: ReasoningStep) -> Dict[str, Any]:
        """Execute query analysis step."""
        query = input_data.get("query", "")
        return self.query_analyzer.analyze_query(query)
    
    def _execute_information_retrieval(self, input_data: Dict[str, Any], step: ReasoningStep) -> Dict[str, Any]:
        """Execute information retrieval step."""
        if not self.document_store:
            return {"error": "No document store available", "retrieved_docs": []}
        
        query = input_data.get("query", "")
        key_concepts = input_data.get("key_concepts", [])
        
        # Search for similar documents
        retrieved_docs = self.document_store.search_similar(query, top_k=10)
        
        return {
            "query": query,
            "key_concepts": key_concepts,
            "retrieved_documents": [
                {
                    "id": doc.id,
                    "content": doc.content[:500] + "..." if len(doc.content) > 500 else doc.content,
                    "metadata": doc.metadata,
                    "similarity_score": score
                }
                for doc, score in retrieved_docs
            ],
            "retrieval_count": len(retrieved_docs)
        }
    
    def _execute_fact_extraction(self, input_data: Dict[str, Any], step: ReasoningStep) -> Dict[str, Any]:
        """Execute fact extraction step."""
        retrieved_docs = input_data.get("dep_step_2", {}).get("retrieved_documents", [])
        
        facts = []
        for doc in retrieved_docs:
            content = doc.get("content", "")
            # Simple fact extraction - look for statements that appear factual
            sentences = re.split(r'[.!?]+', content)
            for sentence in sentences:
                sentence = sentence.strip()
                if len(sentence) > 20 and self._is_likely_fact(sentence):
                    facts.append({
                        "fact": sentence,
                        "source_doc": doc.get("id"),
                        "confidence": 0.6
                    })
        
        return {
            "extracted_facts": facts,
            "fact_count": len(facts)
        }
    
    def _execute_logical_deduction(self, input_data: Dict[str, Any], step: ReasoningStep) -> Dict[str, Any]:
        """Execute logical deduction step."""
        facts = input_data.get("dep_step_3", {}).get("extracted_facts", [])
        
        deductions = []
        
        # Simple logical patterns
        for i, fact1 in enumerate(facts):
            for j, fact2 in enumerate(facts[i+1:], i+1):
                # Look for complementary facts
                deduction = self._make_deduction(fact1["fact"], fact2["fact"])
                if deduction:
                    deductions.append({
                        "deduction": deduction,
                        "based_on_facts": [fact1["fact"], fact2["fact"]],
                        "confidence": 0.5
                    })
        
        return {
            "logical_deductions": deductions,
            "deduction_count": len(deductions)
        }
    
    def _execute_synthesis(self, input_data: Dict[str, Any], step: ReasoningStep) -> Dict[str, Any]:
        """Execute synthesis step."""
        # Gather all relevant information
        retrieved_docs = input_data.get("dep_step_2", {}).get("retrieved_documents", [])
        facts = input_data.get("dep_step_3", {}).get("extracted_facts", [])
        deductions = input_data.get("dep_step_4", {}).get("logical_deductions", [])
        
        # Synthesize information
        synthesis = {
            "retrieved_information_count": len(retrieved_docs),
            "extracted_facts_count": len(facts),
            "logical_deductions_count": len(deductions),
            "key_points": self._extract_key_points(retrieved_docs, facts, deductions),
            "information_gaps": self._identify_information_gaps(retrieved_docs, facts)
        }
        
        return synthesis
    
    def _execute_conclusion(self, input_data: Dict[str, Any], step: ReasoningStep) -> Dict[str, Any]:
        """Execute conclusion step."""
        retrieved_docs = input_data.get("dep_step_2", {}).get("retrieved_documents", [])
        
        conclusion = {
            "answer_summary": self._generate_answer_summary(retrieved_docs),
            "confidence_assessment": self._assess_answer_confidence(retrieved_docs),
            "limitations": self._identify_limitations(retrieved_docs)
        }
        
        return conclusion
    
    def _execute_evidence_evaluation(self, input_data: Dict[str, Any], step: ReasoningStep) -> Dict[str, Any]:
        """Execute evidence evaluation step."""
        # Placeholder for evidence evaluation
        return {"evaluation": "Evidence evaluation not yet implemented"}
    
    def _execute_hypothesis_generation(self, input_data: Dict[str, Any], step: ReasoningStep) -> Dict[str, Any]:
        """Execute hypothesis generation step."""
        # Placeholder for hypothesis generation
        return {"hypotheses": []}
    
    def _generate_final_answer(self, plan: ReasoningPlan) -> str:
        """Generate the final answer from the reasoning plan."""
        if not plan.steps:
            return "No reasoning steps were executed."
        
        # Get the final step's output
        final_step = plan.steps[-1]
        
        if final_step.step_type == ReasoningStepType.CONCLUSION:
            conclusion_data = final_step.output_data
            summary = conclusion_data.get("answer_summary", "No summary available.")
            confidence = conclusion_data.get("confidence_assessment", "Unknown confidence")
            limitations = conclusion_data.get("limitations", [])
            
            answer = f"{summary}\n\nConfidence: {confidence}"
            if limitations:
                answer += f"\n\nLimitations: {', '.join(limitations)}"
            
            return answer
        
        elif final_step.step_type == ReasoningStepType.SYNTHESIS:
            synthesis_data = final_step.output_data
            key_points = synthesis_data.get("key_points", [])
            gaps = synthesis_data.get("information_gaps", [])
            
            answer = "Based on the analysis and synthesis of retrieved information:\n\n"
            if key_points:
                answer += "Key Points:\n" + "\n".join(f"- {point}" for point in key_points) + "\n\n"
            
            if gaps:
                answer += "Information Gaps:\n" + "\n".join(f"- {gap}" for gap in gaps)
            
            return answer
        
        else:
            return "Reasoning completed but final answer generation not implemented for this step type."
    
    def _calculate_confidence_score(self, plan: ReasoningPlan) -> float:
        """Calculate overall confidence score for the reasoning plan."""
        if not plan.steps:
            return 0.0
        
        # Average confidence of all steps
        total_confidence = sum(step.confidence for step in plan.steps)
        return total_confidence / len(plan.steps)
    
    # Helper methods
    def _is_likely_fact(self, sentence: str) -> bool:
        """Determine if a sentence is likely a factual statement."""
        # Simple heuristics
        fact_indicators = ['is', 'are', 'was', 'were', 'has', 'have', 'had', 'can', 'could', 'will', 'would']
        question_indicators = ['?', 'who', 'what', 'when', 'where', 'why', 'how']
        
        has_fact_indicator = any(indicator in sentence.lower() for indicator in fact_indicators)
        has_question_indicator = any(indicator in sentence.lower() for indicator in question_indicators)
        
        return has_fact_indicator and not has_question_indicator
    
    def _make_deduction(self, fact1: str, fact2: str) -> Optional[str]:
        """Make a simple deduction from two facts."""
        # Very simple deduction logic
        if "increase" in fact1.lower() and "decrease" in fact2.lower():
            return f"There may be an inverse relationship between the concepts in: '{fact1}' and '{fact2}'"
        
        if "similar" in fact1.lower() and "similar" in fact2.lower():
            return f"Both facts indicate similarity: '{fact1}' and '{fact2}'"
        
        return None
    
    def _extract_key_points(self, docs: List[Dict], facts: List[Dict], deductions: List[Dict]) -> List[str]:
        """Extract key points from reasoning results."""
        key_points = []
        
        # Add top document summaries
        for doc in docs[:3]:
            content = doc.get("content", "")
            if content:
                key_points.append(f"From document {doc.get('id')}: {content[:100]}...")
        
        # Add key facts
        for fact in facts[:3]:
            key_points.append(f"Key fact: {fact['fact']}")
        
        # Add deductions
        for deduction in deductions[:2]:
            key_points.append(f"Deduction: {deduction['deduction']}")
        
        return key_points
    
    def _identify_information_gaps(self, docs: List[Dict], facts: List[Dict]) -> List[str]:
        """Identify gaps in the retrieved information."""
        gaps = []
        
        if not docs:
            gaps.append("No relevant documents found")
        
        if len(facts) < 3:
            gaps.append("Limited factual information extracted")
        
        return gaps
    
    def _generate_answer_summary(self, docs: List[Dict]) -> str:
        """Generate a summary answer from retrieved documents."""
        if not docs:
            return "No relevant information was found to answer the query."
        
        # Simple summary based on top documents
        top_doc = docs[0]
        content = top_doc.get("content", "")
        
        if len(content) > 300:
            summary = content[:300] + "..."
        else:
            summary = content
        
        return f"Based on the most relevant document found: {summary}"
    
    def _assess_answer_confidence(self, docs: List[Dict]) -> str:
        """Assess the confidence in the answer."""
        if not docs:
            return "Very Low"
        elif len(docs) == 1:
            return "Low"
        elif len(docs) < 5:
            return "Medium"
        else:
            return "High"
    
    def _identify_limitations(self, docs: List[Dict]) -> List[str]:
        """Identify limitations in the answer."""
        limitations = []
        
        if len(docs) < 3:
            limitations.append("Limited source documents")
        
        if not docs:
            limitations.append("No relevant information found")
        
        return limitations
    
    def get_reasoning_history(self) -> List[ReasoningPlan]:
        """Get the history of reasoning plans."""
        return self.reasoning_history
    
    def clear_history(self):
        """Clear the reasoning history."""
        self.reasoning_history.clear()
