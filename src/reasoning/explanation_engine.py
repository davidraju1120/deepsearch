import logging
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime
import json

from .reasoning_engine import ReasoningPlan, ReasoningStep, ReasoningStepType

@dataclass
class Explanation:
    """Explanation of reasoning steps and processes."""
    step_id: str
    step_type: str
    explanation: str
    purpose: str
    methodology: str
    inputs_used: List[str]
    outputs_generated: List[str]
    confidence_factors: List[str]
    limitations: List[str]
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "step_id": self.step_id,
            "step_type": self.step_type,
            "explanation": self.explanation,
            "purpose": self.purpose,
            "methodology": self.methodology,
            "inputs_used": self.inputs_used,
            "outputs_generated": self.outputs_generated,
            "confidence_factors": self.confidence_factors,
            "limitations": self.limitations,
            "timestamp": self.timestamp.isoformat()
        }

class ReasoningExplanationEngine:
    """
    Engine for explaining reasoning steps and AI decision-making processes.
    """
    
    def __init__(self):
        """Initialize the explanation engine."""
        self.explanation_templates = self._load_explanation_templates()
        logging.info("ReasoningExplanationEngine initialized")
    
    def explain_reasoning_plan(self, plan: ReasoningPlan) -> Dict[str, Any]:
        """
        Explain the entire reasoning plan.
        
        Args:
            plan: ReasoningPlan to explain
            
        Returns:
            Comprehensive explanation dictionary
        """
        try:
            # Explain each step
            step_explanations = []
            for step in plan.steps:
                explanation = self.explain_reasoning_step(step)
                step_explanations.append(explanation.to_dict())
            
            # Create overall plan explanation
            plan_explanation = {
                "query": plan.query,
                "plan_overview": self._explain_plan_overview(plan),
                "step_count": len(plan.steps),
                "execution_order": plan.execution_order,
                "step_explanations": step_explanations,
                "overall_confidence": plan.confidence_score,
                "complexity_assessment": self._assess_plan_complexity(plan),
                "reasoning_approach": self._describe_reasoning_approach(plan)
            }
            
            return plan_explanation
            
        except Exception as e:
            logging.error(f"Error explaining reasoning plan: {e}")
            return {"error": str(e)}
    
    def explain_reasoning_step(self, step: ReasoningStep) -> Explanation:
        """
        Explain a single reasoning step.
        
        Args:
            step: ReasoningStep to explain
            
        Returns:
            Explanation object
        """
        try:
            # Get template for this step type
            template = self.explanation_templates.get(step.step_type, {})
            
            # Generate explanation components
            explanation = self._generate_step_explanation(step, template)
            purpose = self._generate_step_purpose(step, template)
            methodology = self._generate_step_methodology(step, template)
            inputs_used = self._identify_step_inputs(step)
            outputs_generated = self._identify_step_outputs(step)
            confidence_factors = self._explain_confidence_factors(step)
            limitations = self._explain_step_limitations(step)
            
            return Explanation(
                step_id=step.step_id,
                step_type=step.step_type.value,
                explanation=explanation,
                purpose=purpose,
                methodology=methodology,
                inputs_used=inputs_used,
                outputs_generated=outputs_generated,
                confidence_factors=confidence_factors,
                limitations=limitations
            )
            
        except Exception as e:
            logging.error(f"Error explaining reasoning step {step.step_id}: {e}")
            return Explanation(
                step_id=step.step_id,
                step_type=step.step_type.value,
                explanation=f"Error generating explanation: {str(e)}",
                purpose="Unknown",
                methodology="Unknown",
                inputs_used=[],
                outputs_generated=[],
                confidence_factors=[],
                limitations=["Explanation generation failed"]
            )
    
    def explain_query_processing(self, query: str, reasoning_plan: ReasoningPlan) -> str:
        """
        Generate a human-readable explanation of how a query was processed.
        
        Args:
            query: The original query
            reasoning_plan: The reasoning plan that was executed
            
        Returns:
            Human-readable explanation string
        """
        try:
            explanation_parts = []
            
            # Introduction
            explanation_parts.append(f"🔍 Query Analysis: '{query}'")
            explanation_parts.append("")
            
            # Overall approach
            explanation_parts.append("📋 Research Approach:")
            approach = self._describe_reasoning_approach(reasoning_plan)
            explanation_parts.append(f"  {approach}")
            explanation_parts.append("")
            
            # Step-by-step explanation
            explanation_parts.append("🧠 Reasoning Process:")
            for i, step in enumerate(reasoning_plan.steps, 1):
                step_explanation = self.explain_reasoning_step(step)
                explanation_parts.append(f"  Step {i}: {step.step_type.value.replace('_', ' ').title()}")
                explanation_parts.append(f"    Purpose: {step_explanation.purpose}")
                explanation_parts.append(f"    What happened: {step_explanation.explanation}")
                explanation_parts.append("")
            
            # Confidence assessment
            explanation_parts.append("🎯 Confidence Assessment:")
            confidence = reasoning_plan.confidence_score or 0.0
            confidence_level = "High" if confidence > 0.7 else "Medium" if confidence > 0.4 else "Low"
            explanation_parts.append(f"  Overall confidence: {confidence_level} ({confidence:.2f})")
            
            # Limitations
            explanation_parts.append("")
            explanation_parts.append("⚠️  Limitations:")
            limitations = self._identify_plan_limitations(reasoning_plan)
            for limitation in limitations:
                explanation_parts.append(f"  • {limitation}")
            
            return '\n'.join(explanation_parts)
            
        except Exception as e:
            logging.error(f"Error generating query processing explanation: {e}")
            return f"Error generating explanation: {str(e)}"
    
    def generate_step_by_step_report(self, plan: ReasoningPlan) -> str:
        """
        Generate a detailed step-by-step report of the reasoning process.
        
        Args:
            plan: Executed reasoning plan
            
        Returns:
            Detailed report string
        """
        try:
            report_parts = []
            
            # Header
            report_parts.append("=" * 60)
            report_parts.append("DEEP RESEARCHER AGENT - REASONING REPORT")
            report_parts.append("=" * 60)
            report_parts.append(f"Query: {plan.query}")
            report_parts.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            report_parts.append(f"Total Steps: {len(plan.steps)}")
            report_parts.append(f"Overall Confidence: {plan.confidence_score:.2f}")
            report_parts.append("=" * 60)
            report_parts.append("")
            
            # Step details
            for i, step in enumerate(plan.steps, 1):
                explanation = self.explain_reasoning_step(step)
                
                report_parts.append(f"STEP {i}: {step.step_type.value.replace('_', ' ').upper()}")
                report_parts.append("-" * 40)
                report_parts.append(f"Step ID: {step.step_id}")
                report_parts.append(f"Confidence: {step.confidence:.2f}")
                report_parts.append(f"Dependencies: {', '.join(step.dependencies) if step.dependencies else 'None'}")
                report_parts.append("")
                
                report_parts.append("PURPOSE:")
                report_parts.append(f"  {explanation.purpose}")
                report_parts.append("")
                
                report_parts.append("EXPLANATION:")
                report_parts.append(f"  {explanation.explanation}")
                report_parts.append("")
                
                report_parts.append("METHODOLOGY:")
                report_parts.append(f"  {explanation.methodology}")
                report_parts.append("")
                
                if explanation.inputs_used:
                    report_parts.append("INPUTS USED:")
                    for input_item in explanation.inputs_used:
                        report_parts.append(f"  • {input_item}")
                    report_parts.append("")
                
                if explanation.outputs_generated:
                    report_parts.append("OUTPUTS GENERATED:")
                    for output_item in explanation.outputs_generated:
                        report_parts.append(f"  • {output_item}")
                    report_parts.append("")
                
                if explanation.confidence_factors:
                    report_parts.append("CONFIDENCE FACTORS:")
                    for factor in explanation.confidence_factors:
                        report_parts.append(f"  • {factor}")
                    report_parts.append("")
                
                if explanation.limitations:
                    report_parts.append("LIMITATIONS:")
                    for limitation in explanation.limitations:
                        report_parts.append(f"  • {limitation}")
                    report_parts.append("")
                
                report_parts.append("=" * 60)
                report_parts.append("")
            
            # Final answer
            if plan.final_answer:
                report_parts.append("FINAL ANSWER:")
                report_parts.append("-" * 20)
                report_parts.append(plan.final_answer)
                report_parts.append("")
            
            return '\n'.join(report_parts)
            
        except Exception as e:
            logging.error(f"Error generating step-by-step report: {e}")
            return f"Error generating report: {str(e)}"
    
    def _load_explanation_templates(self) -> Dict[ReasoningStepType, Dict[str, str]]:
        """Load explanation templates for different step types."""
        return {
            ReasoningStepType.QUERY_ANALYSIS: {
                "explanation": "The query was analyzed to understand its complexity, key concepts, and required operations. This helps determine the appropriate research approach.",
                "purpose": "To understand the query requirements and plan the research strategy",
                "methodology": "Natural language processing techniques including keyword extraction, complexity assessment, and query type identification",
                "confidence_factors": ["Query clarity", "Keyword specificity", "Domain familiarity"],
                "limitations": ["May miss nuanced requirements", "Limited by query phrasing"]
            },
            ReasoningStepType.INFORMATION_RETRIEVAL: {
                "explanation": "Relevant documents were retrieved from the knowledge base using semantic similarity search based on the query embedding.",
                "purpose": "To gather relevant information that can help answer the query",
                "methodology": "Embedding-based similarity search using vector database",
                "confidence_factors": ["Document relevance", "Search algorithm effectiveness", "Knowledge base coverage"],
                "limitations": ["Dependent on available documents", "May miss relevant information not in database"]
            },
            ReasoningStepType.FACT_EXTRACTION: {
                "explanation": "Key facts and statements were extracted from the retrieved documents to identify important information points.",
                "purpose": "To identify and extract factual information from source documents",
                "methodology": "Pattern recognition and linguistic analysis to identify factual statements",
                "confidence_factors": ["Source document reliability", "Fact clarity", "Extraction accuracy"],
                "limitations": ["May extract incorrect facts", "Limited by document quality"]
            },
            ReasoningStepType.LOGICAL_DEDUCTION: {
                "explanation": "Logical relationships between facts were analyzed to derive new insights and connections.",
                "purpose": "To reason beyond explicit facts and derive new understanding",
                "methodology": "Logical inference and pattern recognition across multiple facts",
                "confidence_factors": ["Fact reliability", "Logical soundness", "Pattern strength"],
                "limitations": ["May make incorrect inferences", "Limited by available facts"]
            },
            ReasoningStepType.HYPOTHESIS_GENERATION: {
                "explanation": "Potential hypotheses or explanations were generated based on the available information and patterns.",
                "purpose": "To propose possible explanations or solutions",
                "methodology": "Pattern recognition and hypothesis formulation based on evidence",
                "confidence_factors": ["Evidence strength", "Pattern consistency", "Domain knowledge"],
                "limitations": ["Hypotheses may be speculative", "Limited by available data"]
            },
            ReasoningStepType.EVIDENCE_EVALUATION: {
                "explanation": "The strength and reliability of evidence were assessed to determine confidence in different information sources.",
                "purpose": "To evaluate the quality and reliability of available evidence",
                "methodology": "Source credibility assessment and evidence strength analysis",
                "confidence_factors": ["Source credibility", "Evidence consistency", "Methodological rigor"],
                "limitations": ["Subjective assessment", "Limited source information"]
            },
            ReasoningStepType.SYNTHESIS: {
                "explanation": "Information from multiple sources and reasoning steps was combined into a coherent understanding.",
                "purpose": "To integrate diverse information into a unified understanding",
                "methodology": "Information integration and pattern synthesis across multiple sources",
                "confidence_factors": ["Information consistency", "Source diversity", "Integration quality"],
                "limitations": ["May miss contradictions", "Integration challenges"]
            },
            ReasoningStepType.CONCLUSION: {
                "explanation": "A final conclusion was formulated based on the reasoning process and available information.",
                "purpose": "To provide a definitive answer to the original query",
                "methodology": "Conclusion formulation based on reasoning outcomes and evidence",
                "confidence_factors": ["Evidence strength", "Reasoning quality", "Answer completeness"],
                "limitations": ["May be incomplete", "Confidence limited by available information"]
            }
        }
    
    def _generate_step_explanation(self, step: ReasoningStep, template: Dict[str, str]) -> str:
        """Generate explanation for a specific step."""
        base_explanation = template.get("explanation", "No explanation available.")
        
        # Add step-specific details
        if step.step_type == ReasoningStepType.INFORMATION_RETRIEVAL:
            retrieved_count = step.output_data.get("retrieval_count", 0)
            if retrieved_count > 0:
                base_explanation += f" Retrieved {retrieved_count} relevant documents."
        
        elif step.step_type == ReasoningStepType.FACT_EXTRACTION:
            fact_count = step.output_data.get("fact_count", 0)
            if fact_count > 0:
                base_explanation += f" Extracted {fact_count} key facts."
        
        elif step.step_type == ReasoningStepType.LOGICAL_DEDUCTION:
            deduction_count = step.output_data.get("deduction_count", 0)
            if deduction_count > 0:
                base_explanation += f" Made {deduction_count} logical deductions."
        
        return base_explanation
    
    def _generate_step_purpose(self, step: ReasoningStep, template: Dict[str, str]) -> str:
        """Generate purpose explanation for a step."""
        return template.get("purpose", "Purpose not specified.")
    
    def _generate_step_methodology(self, step: ReasoningStep, template: Dict[str, str]) -> str:
        """Generate methodology explanation for a step."""
        return template.get("methodology", "Methodology not specified.")
    
    def _identify_step_inputs(self, step: ReasoningStep) -> List[str]:
        """Identify inputs used by a step."""
        inputs = []
        
        # Add query if present
        if "query" in step.input_data:
            inputs.append("Original query")
        
        # Add key concepts if present
        if "key_concepts" in step.input_data:
            concepts = step.input_data["key_concepts"]
            if concepts:
                inputs.append(f"Key concepts: {', '.join(concepts[:3])}")
        
        # Add dependency information
        if step.dependencies:
            inputs.append(f"Depends on steps: {', '.join(step.dependencies)}")
        
        return inputs
    
    def _identify_step_outputs(self, step: ReasoningStep) -> List[str]:
        """Identify outputs generated by a step."""
        outputs = []
        
        # Common outputs based on step type
        if step.step_type == ReasoningStepType.QUERY_ANALYSIS:
            outputs.extend(["Query complexity assessment", "Key concepts identified", "Required operations"])
        
        elif step.step_type == ReasoningStepType.INFORMATION_RETRIEVAL:
            retrieved_count = step.output_data.get("retrieval_count", 0)
            outputs.append(f"Retrieved {retrieved_count} documents")
            if retrieved_count > 0:
                outputs.append("Similarity scores calculated")
        
        elif step.step_type == ReasoningStepType.FACT_EXTRACTION:
            fact_count = step.output_data.get("fact_count", 0)
            outputs.append(f"Extracted {fact_count} facts")
        
        elif step.step_type == ReasoningStepType.LOGICAL_DEDUCTION:
            deduction_count = step.output_data.get("deduction_count", 0)
            outputs.append(f"Generated {deduction_count} deductions")
        
        elif step.step_type == ReasoningStepType.SYNTHESIS:
            outputs.extend(["Integrated information", "Key points identified", "Information gaps noted"])
        
        elif step.step_type == ReasoningStepType.CONCLUSION:
            outputs.extend(["Final answer generated", "Confidence assessment", "Limitations identified"])
        
        return outputs
    
    def _explain_confidence_factors(self, step: ReasoningStep) -> List[str]:
        """Explain factors affecting confidence for a step."""
        template = self.explanation_templates.get(step.step_type, {})
        base_factors = template.get("confidence_factors", [])
        
        # Add step-specific factors
        if step.step_type == ReasoningStepType.INFORMATION_RETRIEVAL:
            retrieved_count = step.output_data.get("retrieval_count", 0)
            if retrieved_count == 0:
                base_factors.append("No documents retrieved")
            elif retrieved_count < 3:
                base_factors.append("Limited document coverage")
        
        elif step.step_type == ReasoningStepType.FACT_EXTRACTION:
            fact_count = step.output_data.get("fact_count", 0)
            if fact_count == 0:
                base_factors.append("No facts extracted")
        
        return base_factors
    
    def _explain_step_limitations(self, step: ReasoningStep) -> List[str]:
        """Explain limitations of a step."""
        template = self.explanation_templates.get(step.step_type, {})
        return template.get("limitations", [])
    
    def _explain_plan_overview(self, plan: ReasoningPlan) -> str:
        """Explain the overall reasoning plan."""
        step_count = len(plan.steps)
        step_types = [step.step_type.value for step in plan.steps]
        
        overview = f"This reasoning plan consists of {step_count} steps: "
        overview += ", ".join(step_types)
        overview += f". The plan follows a logical sequence to comprehensively address the query."
        
        return overview
    
    def _assess_plan_complexity(self, plan: ReasoningPlan) -> str:
        """Assess the complexity of the reasoning plan."""
        step_count = len(plan.steps)
        
        if step_count <= 2:
            return "Simple - Direct information retrieval and answer generation"
        elif step_count <= 4:
            return "Moderate - Multi-step reasoning with fact extraction and analysis"
        else:
            return "Complex - Comprehensive reasoning with multiple analysis stages"
    
    def _describe_reasoning_approach(self, plan: ReasoningPlan) -> str:
        """Describe the overall reasoning approach."""
        step_types = [step.step_type for step in plan.steps]
        
        if ReasoningStepType.SYNTHESIS in step_types:
            return "Comprehensive synthesis approach - Integrates multiple information sources and reasoning steps"
        elif ReasoningStepType.LOGICAL_DEDUCTION in step_types:
            return "Analytical reasoning approach - Uses logical deduction to derive insights"
        elif ReasoningStepType.FACT_EXTRACTION in step_types:
            return "Fact-based approach - Extracts and analyzes key facts from sources"
        else:
            return "Direct retrieval approach - Retrieves and presents relevant information"
    
    def _identify_plan_limitations(self, plan: ReasoningPlan) -> List[str]:
        """Identify limitations of the reasoning plan."""
        limitations = []
        
        # Check for common limitations
        step_count = len(plan.steps)
        if step_count <= 2:
            limitations.append("Limited reasoning depth")
        
        # Check for missing step types
        step_types = [step.step_type for step in plan.steps]
        if ReasoningStepType.EVIDENCE_EVALUATION not in step_types:
            limitations.append("No explicit evidence evaluation")
        
        if ReasoningStepType.HYPOTHESIS_GENERATION not in step_types:
            limitations.append("No hypothesis generation")
        
        # Check confidence
        if plan.confidence_score and plan.confidence_score < 0.5:
            limitations.append("Low overall confidence in results")
        
        return limitations
    
    def explain_reasoning(self, query_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Explain the reasoning for a query result.
        
        Args:
            query_result: Query result dictionary
            
        Returns:
            Reasoning explanation dictionary
        """
        try:
            # Extract information from query result
            original_query = query_result.get('query', 'Unknown query')
            answer = query_result.get('answer', 'No answer available')
            confidence_score = query_result.get('confidence_score', 0.0)
            reasoning_steps = query_result.get('reasoning_steps', [])
            retrieved_documents = query_result.get('retrieved_documents', [])
            
            # Create explanation structure
            explanation = {
                'original_query': original_query,
                'final_answer': answer,
                'confidence_score': confidence_score,
                'steps': [],
                'document_count': len(retrieved_documents),
                'reasoning_summary': self._generate_reasoning_summary(reasoning_steps, retrieved_documents)
            }
            
            # Add step-by-step explanations
            for i, step in enumerate(reasoning_steps, 1):
                step_explanation = {
                    'step_number': i,
                    'step_type': step.get('type', 'Unknown'),
                    'description': step.get('description', 'No description'),
                    'purpose': step.get('purpose', 'Process information'),
                    'outcome': step.get('outcome', 'Completed')
                }
                explanation['steps'].append(step_explanation)
            
            # If no reasoning steps available, create a basic explanation
            if not reasoning_steps:
                explanation['steps'] = [{
                    'step_number': 1,
                    'step_type': 'Information Retrieval',
                    'description': 'Retrieved relevant documents from knowledge base',
                    'purpose': 'Find information to answer the query',
                    'outcome': 'Completed'
                }]
            
            return explanation
            
        except Exception as e:
            logging.error(f"Error explaining reasoning: {e}")
            return {
                'error': str(e),
                'original_query': query_result.get('query', 'Unknown'),
                'final_answer': 'Error generating explanation',
                'steps': [],
                'document_count': 0
            }
    
    def _generate_reasoning_summary(self, reasoning_steps: List[Dict], retrieved_documents: List[Dict]) -> str:
        """
        Generate a summary of the reasoning process.
        
        Args:
            reasoning_steps: List of reasoning steps
            retrieved_documents: List of retrieved documents
            
        Returns:
            Summary string
        """
        if not reasoning_steps:
            return f"Retrieved {len(retrieved_documents)} documents and provided direct answer based on available information."
        
        step_count = len(reasoning_steps)
        doc_count = len(retrieved_documents)
        
        summary = f"Processed query through {step_count} reasoning steps using {doc_count} relevant documents. "
        
        if step_count <= 2:
            summary += "Used straightforward information retrieval and analysis."
        elif step_count <= 4:
            summary += "Applied multi-step reasoning with fact extraction and synthesis."
        else:
            summary += "Executed comprehensive reasoning with multiple analysis stages."
        
        return summary
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about the reasoning explanation engine.
        
        Returns:
            Dictionary containing explanation engine statistics
        """
        try:
            stats = {
                "status": "active",
                "capabilities": {
                    "step_explanation": True,
                    "plan_explanation": True,
                    "confidence_analysis": True,
                    "limitation_identification": True,
                    "template_based": True
                },
                "explanation_templates": len(self.explanation_templates),
                "supported_step_types": [
                    "information_retrieval",
                    "analysis",
                    "synthesis",
                    "evaluation",
                    "hypothesis_generation",
                    "evidence_evaluation",
                    "conclusion"
                ],
                "explanation_features": {
                    "purpose_explanation": True,
                    "methodology_description": True,
                    "input_output_tracking": True,
                    "confidence_factors": True,
                    "limitation_analysis": True
                },
                "performance_metrics": {
                    "explanations_generated": 0,
                    "average_explanation_length": 0,
                    "template_usage_stats": {}
                }
            }
            
            # Count template usage (if available)
            for template_type in self.explanation_templates:
                stats["performance_metrics"]["template_usage_stats"][template_type] = 0
            
            return stats
            
        except Exception as e:
            logging.error(f"Error getting explanation engine statistics: {e}")
            return {
                "error": str(e),
                "status": "error"
            }
