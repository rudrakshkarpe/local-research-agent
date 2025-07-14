import streamlit as st
import uuid
import threading
from datetime import datetime
from typing import Optional

# Configure Streamlit page
st.set_page_config(
    page_title="🔬 Deep Research Platform",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Import modules
from config import research_config
from research import create_research_graph, ResearchState, ResearchSession
from storage import create_vector_store
from components import (
    display_research_progress,
    display_step_details,
    display_research_metrics,
    render_configuration_sidebar,
    render_research_history_sidebar,
    render_system_status_sidebar,
    render_help_sidebar
)

# Custom CSS for beautiful UI
st.markdown("""
<style>
    .main-header {
        text-align: center;
        padding: 2rem 0;
        background: linear-gradient(90deg, #1f77b4, #17a2b8);
        color: white;
        border-radius: 10px;
        margin-bottom: 2rem;
    }
    
    .research-card {
        background: #f8f9fa;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 4px solid #1f77b4;
        margin: 1rem 0;
        color: #212529;
        font-weight: 500;
    }
    
    .research-card h4 {
        color: #1a1a1a !important;
        font-weight: 600 !important;
        margin-bottom: 0.5rem !important;
    }
    
    .research-card p {
        color: #495057 !important;
        margin-bottom: 0.25rem !important;
    }
    
    .research-card small {
        color: #6c757d !important;
        font-weight: 500 !important;
    }
    
    .metric-card {
        background: white;
        padding: 1rem;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        text-align: center;
    }
    
    .stButton > button {
        background: linear-gradient(90deg, #1f77b4, #17a2b8);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.5rem 2rem;
        font-weight: bold;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
    }
    
    .research-input {
        font-size: 1.1rem;
        padding: 1rem;
        border-radius: 8px;
        border: 2px solid #e9ecef;
    }
    
    .research-input:focus {
        border-color: #1f77b4;
        box-shadow: 0 0 0 0.2rem rgba(31, 119, 180, 0.25);
    }
</style>
""", unsafe_allow_html=True)

def initialize_session_state():
    """Initialize Streamlit session state variables."""
    if 'research_state' not in st.session_state:
        st.session_state.research_state = None
    
    if 'research_config' not in st.session_state:
        st.session_state.research_config = research_config
    
    if 'vector_store' not in st.session_state:
        st.session_state.vector_store = create_vector_store(research_config)
    
    if 'research_running' not in st.session_state:
        st.session_state.research_running = False
    
    if 'selected_session' not in st.session_state:
        st.session_state.selected_session = None
    
    if 'progress_placeholder' not in st.session_state:
        st.session_state.progress_placeholder = None
    
    if 'research_results' not in st.session_state:
        st.session_state.research_results = None
    
    if 'research_error' not in st.session_state:
        st.session_state.research_error = None

def progress_callback(state: ResearchState):
    """Callback function for research progress updates."""
    try:
        # Update session state safely
        st.session_state.research_state = state
    except Exception as e:
        print(f"Progress callback error: {e}")

def run_research_sync(topic: str):
    """Run research synchronously in the main thread."""
    try:
        # Create research graph
        research_graph = create_research_graph(
            st.session_state.research_config,
            progress_callback=progress_callback
        )
        
        # Initialize research state
        research_state = ResearchState(
            research_topic=topic,
            session_id=str(uuid.uuid4()),
            started_at=datetime.now()
        )
        st.session_state.research_state = research_state
        
        # Run the research
        final_state = research_graph.run_research(topic)
        
        # Update final state
        st.session_state.research_state = final_state
        
        # Save to vector store
        if final_state.current_step == "completed":
            session = ResearchSession(
                id=final_state.session_id,
                topic=final_state.research_topic,
                summary=final_state.running_summary,
                sources=final_state.sources_gathered,
                created_at=final_state.started_at,
                completed_at=final_state.completed_at,
                config=st.session_state.research_config.model_dump()
            )
            
            # Save to vector store
            try:
                st.session_state.vector_store.add_session(session)
                st.session_state.research_results = session
            except Exception as ve:
                print(f"Error saving to vector store: {ve}")
        
        st.session_state.research_running = False
        return final_state
        
    except Exception as e:
        print(f"Research error: {e}")
        st.session_state.research_error = str(e)
        st.session_state.research_running = False
        if 'research_state' in st.session_state and st.session_state.research_state:
            st.session_state.research_state.mark_error(str(e))
        return None

def main():
    """Main Streamlit application."""
    
    # Initialize session state
    initialize_session_state()
    
    # Header
    st.markdown("""
        <div class="main-header">
            <h1>🔬 Deep Research Platform</h1>
            <p>AI-Powered Research with Local LLMs</p>
        </div>
    """, unsafe_allow_html=True)
    
    # Sidebar configuration
    updated_config = render_configuration_sidebar(st.session_state.research_config)
    
    # Update config if changed
    if updated_config != st.session_state.research_config:
        st.session_state.research_config = updated_config
        # Recreate vector store with new config
        st.session_state.vector_store = create_vector_store(updated_config)
    
    # Render sidebar components
    render_research_history_sidebar(st.session_state.vector_store)
    render_system_status_sidebar(st.session_state.vector_store)
    render_help_sidebar()
    
    # Main content area
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Research input section
        st.markdown("### 🎯 Start Your Research")
        
        # Load selected session if any
        if st.session_state.selected_session:
            session = st.session_state.selected_session
            st.info(f"📄 Loaded research session: {session.topic}")
            
            # Display loaded session
            with st.expander("📋 Session Details", expanded=True):
                st.markdown(f"**Topic:** {session.topic}")
                st.markdown(f"**Created:** {session.created_at.strftime('%Y-%m-%d %H:%M:%S')}")
                st.markdown(f"**Sources:** {len(session.sources)}")
                
                # Display summary
                st.markdown("**Summary:**")
                st.markdown(session.summary)
                
                # Display sources
                if session.sources:
                    st.markdown("**Sources:**")
                    for i, source in enumerate(session.sources, 1):
                        st.markdown(f"{i}. {source}")
            
            # Clear selection
            if st.button("🗑️ Clear Selection"):
                st.session_state.selected_session = None
                st.rerun()
        
        else:
            # Research input
            research_topic = st.text_area(
                "What would you like to research?",
                placeholder="Enter your research topic here... (e.g., 'Latest developments in quantum computing', 'Climate change impact on agriculture')",
                height=100,
                key="research_input"
            )
            
            # Research controls
            col_btn1, col_btn2, col_btn3 = st.columns([1, 1, 2])
            
            with col_btn1:
                start_research = st.button(
                    "🚀 Start Research",
                    disabled=not research_topic or st.session_state.research_running,
                    type="primary"
                )
            
            with col_btn2:
                if st.session_state.research_running:
                    if st.button("⏹️ Stop Research"):
                        st.session_state.research_running = False
                        if st.session_state.research_state:
                            st.session_state.research_state.mark_error("Research stopped by user")
            
            with col_btn3:
                if research_topic:
                    # Search for similar research
                    similar_sessions = st.session_state.vector_store.search_similar(
                        research_topic, limit=3, threshold=0.5
                    )
                    
                    if similar_sessions:
                        st.info(f"💡 Found {len(similar_sessions)} similar research sessions")
            
            # Start research
            if start_research and research_topic:
                st.session_state.research_running = True
                st.session_state.research_error = None
                
                with st.spinner("🔍 Starting research..."):
                    # Run research synchronously
                    final_state = run_research_sync(research_topic)
                    
                    if final_state:
                        st.success("✅ Research completed successfully!")
                    else:
                        st.error(f"❌ Research failed: {st.session_state.research_error}")
                
                st.rerun()
        
        # Progress display
        if st.session_state.research_state:
            st.markdown("---")
            st.markdown("### 📊 Research Progress")
            
            # Create progress placeholder
            st.session_state.progress_placeholder = st.empty()
            
            with st.session_state.progress_placeholder.container():
                display_research_progress(st.session_state.research_state)
                display_step_details(st.session_state.research_state)
            
            # Auto-refresh during research
            if st.session_state.research_running:
                st.rerun()
        
        # Results display
        if (st.session_state.research_state and 
            st.session_state.research_state.current_step == "completed" and 
            st.session_state.research_state.running_summary):
            
            st.markdown("---")
            st.markdown("### 📋 Research Results")
            
            # Display final summary
            st.markdown(st.session_state.research_state.running_summary)
            
            # Export options
            st.markdown("### 📥 Export Results")
            col_exp1, col_exp2, col_exp3 = st.columns(3)
            
            with col_exp1:
                st.download_button(
                    "📄 Download as Markdown",
                    data=st.session_state.research_state.running_summary,
                    file_name=f"research_{st.session_state.research_state.research_topic[:30]}.md",
                    mime="text/markdown"
                )
            
            with col_exp2:
                # Create text version
                text_content = f"Research Topic: {st.session_state.research_state.research_topic}\n\n"
                text_content += st.session_state.research_state.running_summary
                
                st.download_button(
                    "📝 Download as Text",
                    data=text_content,
                    file_name=f"research_{st.session_state.research_state.research_topic[:30]}.txt",
                    mime="text/plain"
                )
            
            with col_exp3:
                if st.button("🔄 Start New Research"):
                    st.session_state.research_state = None
                    st.session_state.research_running = False
                    st.rerun()
    
    with col2:
        # Metrics and status
        if st.session_state.research_state:
            st.markdown("### 📈 Research Metrics")
            display_research_metrics(st.session_state.research_state)
        
        # Recent research sessions
        st.markdown("### 📚 Recent Research")
        recent_sessions = st.session_state.vector_store.get_recent_sessions(limit=3)
        
        if recent_sessions:
            for session in recent_sessions:
                with st.container():
                    st.markdown(f"""
                        <div class="research-card">
                            <h4>📄 {session.topic[:40]}...</h4>
                            <p><small>📅 {session.created_at.strftime('%Y-%m-%d %H:%M')}</small></p>
                            <p><small>📊 {len(session.sources)} sources</small></p>
                        </div>
                    """, unsafe_allow_html=True)
                    
                    if st.button(f"View Details", key=f"view_{session.id}"):
                        st.session_state.selected_session = session
                        st.rerun()
        else:
            st.info("No research history yet. Start your first research!")
        
        # System stats
        st.markdown("### 📊 System Statistics")
        stats = st.session_state.vector_store.get_stats()
        
        if stats:
            st.metric("Total Research Sessions", stats.get("total_sessions", 0))
            st.metric("Recent Activity (7d)", stats.get("recent_sessions", 0))
            st.metric("Vector Embeddings", stats.get("sessions_with_embeddings", 0))

if __name__ == "__main__":
    main()


