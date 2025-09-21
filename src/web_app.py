#!/usr/bin/env python3
"""
Deep Researcher Agent Web Interface
Flask web application for the Deep Researcher Agent
"""
import os
import json
import logging
from pathlib import Path
from flask import Flask, render_template, request, jsonify, send_from_directory
from flask_cors import CORS
from typing import Dict, Any, Optional

# Add the src directory to the path so we can import our modules
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from main import DeepResearcherAgent

app = Flask(__name__, 
           template_folder='../web/templates',
           static_folder='../web/static')
CORS(app)

# Global agent instance
agent = None

def initialize_agent():
    """Initialize the Deep Researcher Agent."""
    global agent
    try:
        agent = DeepResearcherAgent()
        logging.info("Deep Researcher Agent initialized successfully for web interface")
        return True
    except Exception as e:
        logging.error(f"Failed to initialize agent: {e}")
        return False

@app.route('/')
def index():
    """Main page."""
    return render_template('index.html')

@app.route('/api/status')
def get_status():
    """Get system status."""
    try:
        if not agent:
            if not initialize_agent():
                return jsonify({'error': 'Failed to initialize agent'}), 500
        
        status = agent.get_status()
        return jsonify(status)
    except Exception as e:
        logging.error(f"Error getting status: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/query', methods=['POST'])
def process_query():
    """Process a research query."""
    try:
        if not agent:
            if not initialize_agent():
                return jsonify({'error': 'Failed to initialize agent'}), 500
        
        data = request.get_json()
        query = data.get('query', '')
        enable_refinement = data.get('enable_refinement', True)
        enable_summarization = data.get('enable_summarization', True)
        
        if not query:
            return jsonify({'error': 'Query is required'}), 400
        
        # Process the query
        result = agent.query(
            query_text=query,
            enable_refinement=enable_refinement,
            enable_summarization=enable_summarization
        )
        
        return jsonify(result)
    except Exception as e:
        logging.error(f"Error processing query: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/ingest/text', methods=['POST'])
def ingest_text():
    """Ingest text content."""
    try:
        if not agent:
            if not initialize_agent():
                return jsonify({'error': 'Failed to initialize agent'}), 500
        
        data = request.get_json()
        text = data.get('text', '')
        
        if not text:
            return jsonify({'error': 'Text is required'}), 400
        
        # Ingest the text
        doc_id = agent.ingest_text(text)
        
        return jsonify({
            'success': True,
            'document_id': doc_id,
            'message': 'Text ingested successfully'
        })
    except Exception as e:
        logging.error(f"Error ingesting text: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/ingest/file', methods=['POST'])
def ingest_file():
    """Ingest a file."""
    try:
        if not agent:
            if not initialize_agent():
                return jsonify({'error': 'Failed to initialize agent'}), 500
        
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # Save the file temporarily
        upload_dir = Path('../data/uploads')
        upload_dir.mkdir(exist_ok=True)
        
        file_path = upload_dir / file.filename
        file.save(str(file_path))
        
        # Ingest the file
        doc_ids = agent.ingest_file(str(file_path))
        
        # Clean up the temporary file
        file_path.unlink()
        
        return jsonify({
            'success': True,
            'document_ids': doc_ids,
            'message': f'File {file.filename} ingested successfully'
        })
    except Exception as e:
        logging.error(f"Error ingesting file: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/explain', methods=['POST'])
def explain_reasoning():
    """Explain reasoning for a query result."""
    try:
        if not agent:
            if not initialize_agent():
                return jsonify({'error': 'Failed to initialize agent'}), 500
        
        data = request.get_json()
        query_result = data.get('query_result', {})
        
        if not query_result:
            return jsonify({'error': 'Query result is required'}), 400
        
        # Get explanation
        explanation = agent.explain_reasoning(query_result)
        
        return jsonify(explanation)
    except Exception as e:
        logging.error(f"Error explaining reasoning: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/export', methods=['POST'])
def export_result():
    """Export a query result."""
    try:
        if not agent:
            if not initialize_agent():
                return jsonify({'error': 'Failed to initialize agent'}), 500
        
        data = request.get_json()
        query_result = data.get('query_result', {})
        format_type = data.get('format', 'markdown')
        filename = data.get('filename', None)
        
        if not query_result:
            return jsonify({'error': 'Query result is required'}), 400
        
        # Export the result
        export_path = agent.export_query_result(query_result, format_type, filename)
        
        return jsonify({
            'success': True,
            'export_path': export_path,
            'message': f'Result exported successfully to {export_path}'
        })
    except Exception as e:
        logging.error(f"Error exporting result: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/exports')
def list_exports():
    """List all exported files."""
    try:
        if not agent:
            if not initialize_agent():
                return jsonify({'error': 'Failed to initialize agent'}), 500
        
        exports = agent.list_exports()
        
        return jsonify(exports)
    except Exception as e:
        logging.error(f"Error listing exports: {e}")
        return jsonify({'error': str(e)}), 500

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors."""
    return jsonify({'error': 'Not found'}), 404

@app.route('/api/deep-research', methods=['POST'])
def deep_research():
    """Perform deep research with web search capabilities."""
    try:
        if not agent:
            if not initialize_agent():
                return jsonify({'error': 'Failed to initialize agent'}), 500

        data = request.get_json()
        query = data.get('query', '')
        original_result = data.get('original_result', {})

        if not query:
            return jsonify({'error': 'Query is required'}), 400

        # Perform web search and analysis
        deep_results = agent.perform_deep_research(query, original_result)

        return jsonify(deep_results)

    except Exception as e:
        logging.error(f"Error performing deep research: {e}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    # Setup logging
    logging.basicConfig(level=logging.INFO)
    
    # Initialize the agent
    if initialize_agent():
        print("🚀 Deep Researcher Agent Web Interface starting...")
        print("📱 Open your browser and go to: http://localhost:5000")
        print("🛑 Press Ctrl+C to stop the server")
        
        # Run the Flask app
        app.run(debug=True, host='0.0.0.0', port=5000)
    else:
        print("❌ Failed to initialize Deep Researcher Agent")
        sys.exit(1)
