#!/usr/bin/env python3
"""
Test script to verify the research functionality works end-to-end.
"""

import sys
import os
sys.path.insert(0, '.')

from config import research_config
from research import create_research_graph, ResearchState
from storage import create_vector_store
import uuid
from datetime import datetime

def test_research():
    """Test the research functionality."""
    print("🔬 Testing Deep Research Platform...")
    print("=" * 50)
    
    # Test topic
    topic = "Climate change impact on agriculture"
    print(f"📝 Research Topic: {topic}")
    
    try:
        # Test configuration
        print(f"⚙️  LLM Provider: {research_config.llm_provider}")
        print(f"🤖 Model: {research_config.local_llm}")
        print(f"🔗 Ollama URL: {research_config.ollama_base_url}")
        print(f"🔍 Search API: {research_config.search_api}")
        
        # Test vector store
        print("\n📊 Testing Vector Store...")
        vector_store = create_vector_store(research_config)
        stats = vector_store.get_stats()
        print(f"✅ Vector store initialized: {stats}")
        
        # Test research graph creation
        print("\n🔧 Creating Research Graph...")
        research_graph = create_research_graph(research_config)
        print("✅ Research graph created successfully")
        
        # Test research execution
        print(f"\n🚀 Starting research on: '{topic}'")
        print("This may take a few minutes...")
        
        # Initialize research state
        research_state = ResearchState(
            research_topic=topic,
            session_id=str(uuid.uuid4()),
            started_at=datetime.now()
        )
        
        # Run research
        final_state = research_graph.run_research(topic)
        
        if final_state and final_state.current_step == "completed":
            print("\n✅ Research completed successfully!")
            print(f"📄 Summary length: {len(final_state.running_summary)} characters")
            print(f"📚 Sources found: {len(final_state.sources_gathered)}")
            
            # Display first 500 characters of summary
            print("\n📋 Research Summary (preview):")
            print("-" * 50)
            print(final_state.running_summary[:500] + "..." if len(final_state.running_summary) > 500 else final_state.running_summary)
            print("-" * 50)
            
            # Display sources
            if final_state.sources_gathered:
                print(f"\n📚 Sources ({len(final_state.sources_gathered)}):")
                for i, source in enumerate(final_state.sources_gathered[:5], 1):
                    print(f"{i}. {source}")
                if len(final_state.sources_gathered) > 5:
                    print(f"... and {len(final_state.sources_gathered) - 5} more sources")
            
            print("\n🎉 All tests passed! The research platform is working correctly.")
            return True
            
        else:
            print("❌ Research failed or incomplete")
            return False
            
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_research()
    sys.exit(0 if success else 1)


