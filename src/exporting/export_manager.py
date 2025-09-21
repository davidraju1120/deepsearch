import os
import logging
from typing import List, Dict, Any, Optional, Union
from datetime import datetime
from pathlib import Path
import json
import markdown
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.pdfgen import canvas

from ..querying.query_handler import QueryResult
from ..processing.summarizer import Summary
from ..reasoning.explanation_engine import ReasoningExplanationEngine, ReasoningPlan

class ExportManager:
    """
    Manager for exporting research results in various formats (PDF, Markdown, JSON).
    """
    
    def __init__(self, output_dir: str = "exports"):
        """
        Initialize the export manager.
        
        Args:
            output_dir: Directory to save exported files
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.explanation_engine = ReasoningExplanationEngine()
        logging.info(f"ExportManager initialized with output directory: {self.output_dir}")
    
    def export_query_result(self, query_result: QueryResult, format_type: str = "pdf", 
                          filename: Optional[str] = None) -> str:
        """
        Export a query result to the specified format.
        
        Args:
            query_result: QueryResult to export
            format_type: Export format ('pdf', 'markdown', 'json')
            filename: Optional custom filename
            
        Returns:
            Path to the exported file
        """
        try:
            # Generate filename if not provided
            if not filename:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                safe_query = "".join(c for c in query_result.query[:30] if c.isalnum() or c in (' ', '-', '_')).rstrip()
                safe_query = safe_query.replace(' ', '_')
                filename = f"query_result_{safe_query}_{timestamp}"
            
            # Export based on format type
            if format_type.lower() == "pdf":
                return self._export_query_result_to_pdf(query_result, filename)
            elif format_type.lower() == "markdown":
                return self._export_query_result_to_markdown(query_result, filename)
            elif format_type.lower() == "json":
                return self._export_query_result_to_json(query_result, filename)
            else:
                raise ValueError(f"Unsupported export format: {format_type}")
                
        except Exception as e:
            logging.error(f"Error exporting query result: {e}")
            raise
    
    def export_summary(self, summary: Summary, format_type: str = "pdf", 
                      filename: Optional[str] = None) -> str:
        """
        Export a summary to the specified format.
        
        Args:
            summary: Summary to export
            format_type: Export format ('pdf', 'markdown', 'json')
            filename: Optional custom filename
            
        Returns:
            Path to the exported file
        """
        try:
            # Generate filename if not provided
            if not filename:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"summary_{summary.summary_type}_{timestamp}"
            
            # Export based on format type
            if format_type.lower() == "pdf":
                return self._export_summary_to_pdf(summary, filename)
            elif format_type.lower() == "markdown":
                return self._export_summary_to_markdown(summary, filename)
            elif format_type.lower() == "json":
                return self._export_summary_to_json(summary, filename)
            else:
                raise ValueError(f"Unsupported export format: {format_type}")
                
        except Exception as e:
            logging.error(f"Error exporting summary: {e}")
            raise
    
    def export_reasoning_report(self, reasoning_plan: ReasoningPlan, format_type: str = "pdf",
                               filename: Optional[str] = None) -> str:
        """
        Export a reasoning report to the specified format.
        
        Args:
            reasoning_plan: ReasoningPlan to export
            format_type: Export format ('pdf', 'markdown', 'json')
            filename: Optional custom filename
            
        Returns:
            Path to the exported file
        """
        try:
            # Generate filename if not provided
            if not filename:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                safe_query = "".join(c for c in reasoning_plan.query[:30] if c.isalnum() or c in (' ', '-', '_')).rstrip()
                safe_query = safe_query.replace(' ', '_')
                filename = f"reasoning_report_{safe_query}_{timestamp}"
            
            # Export based on format type
            if format_type.lower() == "pdf":
                return self._export_reasoning_report_to_pdf(reasoning_plan, filename)
            elif format_type.lower() == "markdown":
                return self._export_reasoning_report_to_markdown(reasoning_plan, filename)
            elif format_type.lower() == "json":
                return self._export_reasoning_report_to_json(reasoning_plan, filename)
            else:
                raise ValueError(f"Unsupported export format: {format_type}")
                
        except Exception as e:
            logging.error(f"Error exporting reasoning report: {e}")
            raise
    
    def _export_query_result_to_pdf(self, query_result: QueryResult, filename: str) -> str:
        """Export query result to PDF format."""
        filepath = self.output_dir / f"{filename}.pdf"
        
        try:
            doc = SimpleDocTemplate(str(filepath), pagesize=A4)
            story = []
            styles = getSampleStyleSheet()
            
            # Title
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=16,
                spaceAfter=30,
                textColor=colors.darkblue
            )
            story.append(Paragraph("Deep Researcher Agent - Query Result", title_style))
            story.append(Spacer(1, 12))
            
            # Query information
            story.append(Paragraph(f"<b>Query:</b> {query_result.query}", styles['Normal']))
            story.append(Paragraph(f"<b>Timestamp:</b> {query_result.timestamp.strftime('%Y-%m-%d %H:%M:%S')}", styles['Normal']))
            story.append(Paragraph(f"<b>Confidence:</b> {query_result.confidence:.2f}", styles['Normal']))
            story.append(Paragraph(f"<b>Processing Time:</b> {query_result.processing_time:.2f} seconds", styles['Normal']))
            story.append(Spacer(1, 12))
            
            # Answer
            if query_result.answer:
                story.append(Paragraph("<b>Answer:</b>", styles['Heading2']))
                story.append(Paragraph(query_result.answer, styles['Normal']))
                story.append(Spacer(1, 12))
            
            # Sources
            if query_result.sources:
                story.append(Paragraph("<b>Sources:</b>", styles['Heading2']))
                for i, source in enumerate(query_result.sources, 1):
                    story.append(Paragraph(f"<b>Source {i}:</b>", styles['Heading3']))
                    story.append(Paragraph(f"Document: {source.get('document_id', 'Unknown')}", styles['Normal']))
                    story.append(Paragraph(f"Score: {source.get('score', 0):.3f}", styles['Normal']))
                    if 'content' in source:
                        content_preview = source['content'][:200] + "..." if len(source['content']) > 200 else source['content']
                        story.append(Paragraph(f"Content: {content_preview}", styles['Normal']))
                    story.append(Spacer(1, 6))
                story.append(Spacer(1, 12))
            
            # Reasoning steps
            if query_result.reasoning_steps:
                story.append(Paragraph("<b>Reasoning Steps:</b>", styles['Heading2']))
                for i, step in enumerate(query_result.reasoning_steps, 1):
                    story.append(Paragraph(f"<b>Step {i}:</b> {step.get('step_type', 'Unknown')}", styles['Heading3']))
                    story.append(Paragraph(f"Description: {step.get('description', 'No description')}", styles['Normal']))
                    if 'result' in step:
                        story.append(Paragraph(f"Result: {step['result']}", styles['Normal']))
                    story.append(Spacer(1, 6))
            
            # Build PDF
            doc.build(story)
            logging.info(f"Query result exported to PDF: {filepath}")
            return str(filepath)
            
        except Exception as e:
            logging.error(f"Error creating PDF: {e}")
            raise
    
    def _export_query_result_to_markdown(self, query_result: QueryResult, filename: str) -> str:
        """Export query result to Markdown format."""
        filepath = self.output_dir / f"{filename}.md"
        
        try:
            markdown_content = []
            
            # Header
            markdown_content.append("# Deep Researcher Agent - Query Result")
            markdown_content.append("")
            
            # Query information
            markdown_content.append("## Query Information")
            markdown_content.append(f"- **Query:** {query_result.query}")
            markdown_content.append(f"- **Timestamp:** {query_result.timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
            markdown_content.append(f"- **Confidence:** {query_result.confidence:.2f}")
            markdown_content.append(f"- **Processing Time:** {query_result.processing_time:.2f} seconds")
            markdown_content.append("")
            
            # Answer
            if query_result.answer:
                markdown_content.append("## Answer")
                markdown_content.append(query_result.answer)
                markdown_content.append("")
            
            # Sources
            if query_result.sources:
                markdown_content.append("## Sources")
                for i, source in enumerate(query_result.sources, 1):
                    markdown_content.append(f"### Source {i}")
                    markdown_content.append(f"- **Document:** {source.get('document_id', 'Unknown')}")
                    markdown_content.append(f"- **Score:** {source.get('score', 0):.3f}")
                    if 'content' in source:
                        content_preview = source['content'][:200] + "..." if len(source['content']) > 200 else source['content']
                        markdown_content.append(f"- **Content:** {content_preview}")
                    markdown_content.append("")
            
            # Reasoning steps
            if query_result.reasoning_steps:
                markdown_content.append("## Reasoning Steps")
                for i, step in enumerate(query_result.reasoning_steps, 1):
                    markdown_content.append(f"### Step {i}: {step.get('step_type', 'Unknown')}")
                    markdown_content.append(f"**Description:** {step.get('description', 'No description')}")
                    if 'result' in step:
                        markdown_content.append(f"**Result:** {step['result']}")
                    markdown_content.append("")
            
            # Write to file
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write('\n'.join(markdown_content))
            
            logging.info(f"Query result exported to Markdown: {filepath}")
            return str(filepath)
            
        except Exception as e:
            logging.error(f"Error creating Markdown: {e}")
            raise
    
    def _export_query_result_to_json(self, query_result: QueryResult, filename: str) -> str:
        """Export query result to JSON format."""
        filepath = self.output_dir / f"{filename}.json"
        
        try:
            # Convert to dictionary
            result_dict = {
                "query": query_result.query,
                "timestamp": query_result.timestamp.isoformat(),
                "confidence": query_result.confidence,
                "processing_time": query_result.processing_time,
                "answer": query_result.answer,
                "sources": query_result.sources,
                "reasoning_steps": query_result.reasoning_steps,
                "metadata": query_result.metadata
            }
            
            # Write to file
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(result_dict, f, indent=2, ensure_ascii=False)
            
            logging.info(f"Query result exported to JSON: {filepath}")
            return str(filepath)
            
        except Exception as e:
            logging.error(f"Error creating JSON: {e}")
            raise
    
    def _export_summary_to_pdf(self, summary: Summary, filename: str) -> str:
        """Export summary to PDF format."""
        filepath = self.output_dir / f"{filename}.pdf"
        
        try:
            doc = SimpleDocTemplate(str(filepath), pagesize=A4)
            story = []
            styles = getSampleStyleSheet()
            
            # Title
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=16,
                spaceAfter=30,
                textColor=colors.darkgreen
            )
            story.append(Paragraph("Deep Researcher Agent - Summary", title_style))
            story.append(Spacer(1, 12))
            
            # Summary information
            story.append(Paragraph(f"<b>Summary Type:</b> {summary.summary_type}", styles['Normal']))
            story.append(Paragraph(f"<b>Timestamp:</b> {summary.timestamp.strftime('%Y-%m-%d %H:%M:%S')}", styles['Normal']))
            story.append(Paragraph(f"<b>Source Count:</b> {summary.source_count}", styles['Normal']))
            story.append(Paragraph(f"<b>Confidence:</b> {summary.confidence:.2f}", styles['Normal']))
            story.append(Spacer(1, 12))
            
            # Summary content
            if summary.content:
                story.append(Paragraph("<b>Summary:</b>", styles['Heading2']))
                story.append(Paragraph(summary.content, styles['Normal']))
                story.append(Spacer(1, 12))
            
            # Key points
            if summary.key_points:
                story.append(Paragraph("<b>Key Points:</b>", styles['Heading2']))
                for point in summary.key_points:
                    story.append(Paragraph(f"• {point}", styles['Normal']))
                story.append(Spacer(1, 12))
            
            # Source documents
            if summary.source_documents:
                story.append(Paragraph("<b>Source Documents:</b>", styles['Heading2']))
                for doc in summary.source_documents:
                    story.append(Paragraph(f"• {doc}", styles['Normal']))
                story.append(Spacer(1, 12))
            
            # Build PDF
            doc.build(story)
            logging.info(f"Summary exported to PDF: {filepath}")
            return str(filepath)
            
        except Exception as e:
            logging.error(f"Error creating PDF: {e}")
            raise
    
    def _export_summary_to_markdown(self, summary: Summary, filename: str) -> str:
        """Export summary to Markdown format."""
        filepath = self.output_dir / f"{filename}.md"
        
        try:
            markdown_content = []
            
            # Header
            markdown_content.append("# Deep Researcher Agent - Summary")
            markdown_content.append("")
            
            # Summary information
            markdown_content.append("## Summary Information")
            markdown_content.append(f"- **Summary Type:** {summary.summary_type}")
            markdown_content.append(f"- **Timestamp:** {summary.timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
            markdown_content.append(f"- **Source Count:** {summary.source_count}")
            markdown_content.append(f"- **Confidence:** {summary.confidence:.2f}")
            markdown_content.append("")
            
            # Summary content
            if summary.content:
                markdown_content.append("## Summary")
                markdown_content.append(summary.content)
                markdown_content.append("")
            
            # Key points
            if summary.key_points:
                markdown_content.append("## Key Points")
                for point in summary.key_points:
                    markdown_content.append(f"- {point}")
                markdown_content.append("")
            
            # Source documents
            if summary.source_documents:
                markdown_content.append("## Source Documents")
                for doc in summary.source_documents:
                    markdown_content.append(f"- {doc}")
                markdown_content.append("")
            
            # Write to file
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write('\n'.join(markdown_content))
            
            logging.info(f"Summary exported to Markdown: {filepath}")
            return str(filepath)
            
        except Exception as e:
            logging.error(f"Error creating Markdown: {e}")
            raise
    
    def _export_summary_to_json(self, summary: Summary, filename: str) -> str:
        """Export summary to JSON format."""
        filepath = self.output_dir / f"{filename}.json"
        
        try:
            # Convert to dictionary
            summary_dict = {
                "summary_type": summary.summary_type,
                "timestamp": summary.timestamp.isoformat(),
                "source_count": summary.source_count,
                "confidence": summary.confidence,
                "content": summary.content,
                "key_points": summary.key_points,
                "source_documents": summary.source_documents,
                "metadata": summary.metadata
            }
            
            # Write to file
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(summary_dict, f, indent=2, ensure_ascii=False)
            
            logging.info(f"Summary exported to JSON: {filepath}")
            return str(filepath)
            
        except Exception as e:
            logging.error(f"Error creating JSON: {e}")
            raise
    
    def _export_reasoning_report_to_pdf(self, reasoning_plan: ReasoningPlan, filename: str) -> str:
        """Export reasoning report to PDF format."""
        filepath = self.output_dir / f"{filename}.pdf"
        
        try:
            doc = SimpleDocTemplate(str(filepath), pagesize=A4)
            story = []
            styles = getSampleStyleSheet()
            
            # Title
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=16,
                spaceAfter=30,
                textColor=colors.darkred
            )
            story.append(Paragraph("Deep Researcher Agent - Reasoning Report", title_style))
            story.append(Spacer(1, 12))
            
            # Query information
            story.append(Paragraph(f"<b>Query:</b> {reasoning_plan.query}", styles['Normal']))
            story.append(Paragraph(f"<b>Timestamp:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", styles['Normal']))
            story.append(Paragraph(f"<b>Confidence:</b> {reasoning_plan.confidence_score:.2f}", styles['Normal']))
            story.append(Paragraph(f"<b>Total Steps:</b> {len(reasoning_plan.steps)}", styles['Normal']))
            story.append(Spacer(1, 12))
            
            # Final answer
            if reasoning_plan.final_answer:
                story.append(Paragraph("<b>Final Answer:</b>", styles['Heading2']))
                story.append(Paragraph(reasoning_plan.final_answer, styles['Normal']))
                story.append(Spacer(1, 12))
            
            # Reasoning steps
            story.append(Paragraph("<b>Reasoning Steps:</b>", styles['Heading2']))
            for i, step in enumerate(reasoning_plan.steps, 1):
                story.append(PageBreak())
                story.append(Paragraph(f"<b>Step {i}:</b> {step.step_type.value.replace('_', ' ').title()}", styles['Heading3']))
                story.append(Paragraph(f"<b>Step ID:</b> {step.step_id}", styles['Normal']))
                story.append(Paragraph(f"<b>Confidence:</b> {step.confidence:.2f}", styles['Normal']))
                story.append(Paragraph(f"<b>Dependencies:</b> {', '.join(step.dependencies) if step.dependencies else 'None'}", styles['Normal']))
                story.append(Spacer(1, 6))
                
                # Step explanation
                explanation = self.explanation_engine.explain_reasoning_step(step)
                story.append(Paragraph(f"<b>Purpose:</b> {explanation.purpose}", styles['Normal']))
                story.append(Paragraph(f"<b>Explanation:</b> {explanation.explanation}", styles['Normal']))
                story.append(Spacer(1, 6))
                
                # Inputs and outputs
                if explanation.inputs_used:
                    story.append(Paragraph("<b>Inputs Used:</b>", styles['Normal']))
                    for input_item in explanation.inputs_used:
                        story.append(Paragraph(f"• {input_item}", styles['Normal']))
                    story.append(Spacer(1, 6))
                
                if explanation.outputs_generated:
                    story.append(Paragraph("<b>Outputs Generated:</b>", styles['Normal']))
                    for output_item in explanation.outputs_generated:
                        story.append(Paragraph(f"• {output_item}", styles['Normal']))
                    story.append(Spacer(1, 6))
                
                # Limitations
                if explanation.limitations:
                    story.append(Paragraph("<b>Limitations:</b>", styles['Normal']))
                    for limitation in explanation.limitations:
                        story.append(Paragraph(f"• {limitation}", styles['Normal']))
                    story.append(Spacer(1, 6))
            
            # Build PDF
            doc.build(story)
            logging.info(f"Reasoning report exported to PDF: {filepath}")
            return str(filepath)
            
        except Exception as e:
            logging.error(f"Error creating PDF: {e}")
            raise
    
    def _export_reasoning_report_to_markdown(self, reasoning_plan: ReasoningPlan, filename: str) -> str:
        """Export reasoning report to Markdown format."""
        filepath = self.output_dir / f"{filename}.md"
        
        try:
            # Generate step-by-step report
            report_content = self.explanation_engine.generate_step_by_step_report(reasoning_plan)
            
            # Write to file
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(report_content)
            
            logging.info(f"Reasoning report exported to Markdown: {filepath}")
            return str(filepath)
            
        except Exception as e:
            logging.error(f"Error creating Markdown: {e}")
            raise
    
    def _export_reasoning_report_to_json(self, reasoning_plan: ReasoningPlan, filename: str) -> str:
        """Export reasoning report to JSON format."""
        filepath = self.output_dir / f"{filename}.json"
        
        try:
            # Get explanation
            explanation = self.explanation_engine.explain_reasoning_plan(reasoning_plan)
            
            # Convert to dictionary
            report_dict = {
                "query": reasoning_plan.query,
                "timestamp": datetime.now().isoformat(),
                "confidence_score": reasoning_plan.confidence_score,
                "final_answer": reasoning_plan.final_answer,
                "step_count": len(reasoning_plan.steps),
                "explanation": explanation,
                "steps": []
            }
            
            # Add step details
            for step in reasoning_plan.steps:
                step_dict = {
                    "step_id": step.step_id,
                    "step_type": step.step_type.value,
                    "confidence": step.confidence,
                    "dependencies": step.dependencies,
                    "input_data": step.input_data,
                    "output_data": step.output_data,
                    "execution_time": step.execution_time
                }
                report_dict["steps"].append(step_dict)
            
            # Write to file
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(report_dict, f, indent=2, ensure_ascii=False)
            
            logging.info(f"Reasoning report exported to JSON: {filepath}")
            return str(filepath)
            
        except Exception as e:
            logging.error(f"Error creating JSON: {e}")
            raise
    
    def list_exports(self) -> List[Dict[str, Any]]:
        """
        List all exported files.
        
        Returns:
            List of export information dictionaries
        """
        try:
            exports = []
            
            for file_path in self.output_dir.glob("*"):
                if file_path.is_file():
                    stat = file_path.stat()
                    exports.append({
                        "filename": file_path.name,
                        "filepath": str(file_path),
                        "size": stat.st_size,
                        "created": datetime.fromtimestamp(stat.st_ctime).isoformat(),
                        "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                        "format": file_path.suffix.lower()
                    })
            
            return sorted(exports, key=lambda x: x["created"], reverse=True)
            
        except Exception as e:
            logging.error(f"Error listing exports: {e}")
            return []
    
    def delete_export(self, filename: str) -> bool:
        """
        Delete an exported file.
        
        Args:
            filename: Name of the file to delete
            
        Returns:
            True if successful, False otherwise
        """
        try:
            filepath = self.output_dir / filename
            if filepath.exists():
                filepath.unlink()
                logging.info(f"Deleted export file: {filepath}")
                return True
            else:
                logging.warning(f"Export file not found: {filepath}")
                return False
                
        except Exception as e:
            logging.error(f"Error deleting export file: {e}")
            return False
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about the export manager.
        
        Returns:
            Dictionary containing export manager statistics
        """
        try:
            stats = {
                "status": "active",
                "output_directory": str(self.output_dir),
                "supported_formats": ["pdf", "markdown", "json"],
                "capabilities": {
                    "query_result_export": True,
                    "summary_export": True,
                    "reasoning_plan_export": True,
                    "explanation_export": True,
                    "batch_export": True
                },
                "export_features": {
                    "custom_filenames": True,
                    "file_deletion": True,
                    "format_conversion": True,
                    "metadata_inclusion": True
                },
                "performance_metrics": {
                    "exports_created": 0,
                    "files_deleted": 0,
                    "export_format_usage": {
                        "pdf": 0,
                        "markdown": 0,
                        "json": 0
                    }
                }
            }
            
            # Count existing files in output directory
            if self.output_dir.exists():
                files = list(self.output_dir.glob("*"))
                stats["current_file_count"] = len(files)
                
                # Count by file type
                file_types = {}
                for file in files:
                    ext = file.suffix.lower()
                    if ext in [".pdf", ".md", ".json"]:
                        format_name = ext[1:]  # Remove dot
                        file_types[format_name] = file_types.get(format_name, 0) + 1
                stats["current_files_by_type"] = file_types
            else:
                stats["current_file_count"] = 0
                stats["current_files_by_type"] = {}
            
            return stats
            
        except Exception as e:
            logging.error(f"Error getting export manager statistics: {e}")
            return {
                "error": str(e),
                "status": "error"
            }
