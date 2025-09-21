#!/usr/bin/env python3
"""
Simple startup script for the Deep Researcher Agent Web Interface
"""
import sys
import os

# Add the src directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from web_app import app

if __name__ == '__main__':
    print("🚀 Starting Deep Researcher Agent Web Interface...")
    print("📱 Open your browser and go to: http://localhost:5000")
    print("🛑 Press Ctrl+C to stop the server")
    print("=" * 50)
    
    # Run the Flask app
    app.run(debug=True, host='0.0.0.0', port=5000)
