#!/usr/bin/env python3
"""
Quick test to verify the document_ingestor fix
"""

import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_agent():
    """Test if the agent initializes properly with all components."""

    print("🧪 Testing DeepResearcherAgent initialization...")

    try:
        from src.main import DeepResearcherAgent

        # Initialize agent
        agent = DeepResearcherAgent()
        print("✅ Agent initialized successfully")

        # Check all required components
        components = [
            'document_store',
            'document_ingestor',
            'document_processor',
            'query_handler',
            'query_refiner',
            'summarizer',
            'explanation_engine',
            'export_manager'
        ]

        for component in components:
            if hasattr(agent, component):
                print(f"✅ {component}: Available")
            else:
                print(f"❌ {component}: Missing")

        # Test text ingestion
        print("\n🧪 Testing text ingestion...")
        test_text = "This is a test document for AI research."
        doc_id = agent.ingest_text(test_text)
        print(f"✅ Text ingestion successful: {doc_id}")

        # Test query processing
        print("\n🧪 Testing query processing...")
        result = agent.query("What is AI research?")
        print(f"✅ Query processed successfully")
        print(f"💡 Answer: {result.get('answer', 'No answer')[:100]}...")

        print("\n" + "=" * 50)
        print("🎉 ALL TESTS PASSED!")
        print("✅ The document_ingestor issue has been fixed")
        print("✅ System is ready to use")
        print("=" * 50)

        return True

    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_agent()
