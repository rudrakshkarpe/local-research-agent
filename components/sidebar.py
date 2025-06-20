import streamlit as st
from typing import Dict, Any
from config.settings import ResearchConfig
from research.llm_providers import test_llm_connection

def render_configuration_sidebar(config: ResearchConfig) -> ResearchConfig:
    """Render the configuration sidebar and return updated config."""
    
    st.sidebar.title("🔧 Research Configuration")
    
    # LLM Settings
    st.sidebar.markdown("### 🤖 LLM Settings")
    
    llm_provider = st.sidebar.selectbox(
        "LLM Provider",
        options=["ollama", "lmstudio"],
        index=0 if config.llm_provider == "ollama" else 1,
        help="Choose between Ollama or LMStudio for local LLM"
    )
    
    local_llm = st.sidebar.text_input(
        "Model Name",
        value=config.local_llm,
        help="Name of the local LLM model (e.g., gemma3:latest, llama3.2)"
    )
    
    if llm_provider == "ollama":
        ollama_url = st.sidebar.text_input(
            "Ollama Base URL",
            value=config.ollama_base_url,
            help="Base URL for Ollama API"
        )
        lmstudio_url = config.lmstudio_base_url
    else:
        lmstudio_url = st.sidebar.text_input(
            "LMStudio Base URL",
            value=config.lmstudio_base_url,
            help="Base URL for LMStudio OpenAI-compatible API"
        )
        ollama_url = config.ollama_base_url
    
    # Test LLM Connection
    if st.sidebar.button("🔍 Test LLM Connection"):
        test_config = ResearchConfig(
            llm_provider=llm_provider,
            local_llm=local_llm,
            ollama_base_url=ollama_url,
            lmstudio_base_url=lmstudio_url,
            **{k: v for k, v in config.model_dump().items() 
               if k not in ['llm_provider', 'local_llm', 'ollama_base_url', 'lmstudio_base_url']}
        )
        
        with st.spinner("Testing connection..."):
            result = test_llm_connection(test_config)
            
            if result["status"] == "success":
                st.sidebar.success("✅ LLM connection successful!")
                with st.sidebar.expander("Connection Details"):
                    st.write(f"**Provider:** {result['provider']}")
                    st.write(f"**Model:** {result['model']}")
                    st.write(f"**Base URL:** {result['base_url']}")
            else:
                st.sidebar.error(f"❌ Connection failed: {result['error']}")
    
    st.sidebar.markdown("---")
    
    # Research Settings
    st.sidebar.markdown("### 🔬 Research Settings")
    
    max_loops = st.sidebar.slider(
        "Research Depth",
        min_value=1,
        max_value=10,
        value=config.max_web_research_loops,
        help="Number of research iterations to perform"
    )
    
    search_api_options = ["duckduckgo", "tavily", "perplexity", "searxng"]
    search_api = st.sidebar.selectbox(
        "Search API",
        options=search_api_options,
        index=search_api_options.index(config.search_api) if config.search_api in search_api_options else 0,
        help="Web search API to use for research"
    )
    
    fetch_full_page = st.sidebar.checkbox(
        "Fetch Full Page Content",
        value=config.fetch_full_page,
        help="Include full page content in search results (slower but more comprehensive)"
    )
    
    strip_thinking = st.sidebar.checkbox(
        "Strip Thinking Tokens",
        value=config.strip_thinking_tokens,
        help="Remove <think> tokens from LLM responses"
    )
    
    st.sidebar.markdown("---")
    
    # API Keys
    st.sidebar.markdown("### 🔑 API Keys")
    
    tavily_key = st.sidebar.text_input(
        "Tavily API Key",
        value=config.tavily_api_key or "",
        type="password",
        help="Required for Tavily search API"
    )
    
    perplexity_key = st.sidebar.text_input(
        "Perplexity API Key",
        value=config.perplexity_api_key or "",
        type="password",
        help="Required for Perplexity search API"
    )
    
    searxng_url = st.sidebar.text_input(
        "SearXNG URL",
        value=config.searxng_url,
        help="URL for SearXNG instance"
    )
    
    st.sidebar.markdown("---")
    
    # Vector Embeddings
    st.sidebar.markdown("### 🧠 Vector Embeddings")
    
    embedding_options = [
        "all-MiniLM-L6-v2",
        "all-mpnet-base-v2",
        "sentence-transformers/all-MiniLM-L12-v2",
        "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
    ]
    embedding_model = st.sidebar.selectbox(
        "Embedding Model",
        options=embedding_options,
        index=embedding_options.index(config.embedding_model) if config.embedding_model in embedding_options else 0,
        help="Sentence transformer model for generating embeddings"
    )
    
    st.sidebar.markdown("---")
    
    # Advanced Settings
    with st.sidebar.expander("⚙️ Advanced Settings"):
        st.markdown("**Embedding Dimension**")
        st.text(f"{config.embedding_dimension} (auto-detected)")
        
        st.markdown("**Configuration Export**")
        if st.button("📥 Export Config"):
            config_dict = {
                "llm_provider": llm_provider,
                "local_llm": local_llm,
                "ollama_base_url": ollama_url,
                "lmstudio_base_url": lmstudio_url,
                "max_web_research_loops": max_loops,
                "search_api": search_api,
                "fetch_full_page": fetch_full_page,
                "strip_thinking_tokens": strip_thinking,
                "embedding_model": embedding_model
            }
            st.download_button(
                "Download config.json",
                data=str(config_dict),
                file_name="research_config.json",
                mime="application/json"
            )
    
    # Create updated config
    updated_config = ResearchConfig(
        max_web_research_loops=max_loops,
        local_llm=local_llm,
        llm_provider=llm_provider,
        ollama_base_url=ollama_url,
        lmstudio_base_url=lmstudio_url,
        search_api=search_api,
        fetch_full_page=fetch_full_page,
        strip_thinking_tokens=strip_thinking,
        tavily_api_key=tavily_key if tavily_key else None,
        perplexity_api_key=perplexity_key if perplexity_key else None,
        searxng_url=searxng_url,
        embedding_model=embedding_model,
        embedding_dimension=config.embedding_dimension
    )
    
    return updated_config

def render_research_history_sidebar(vector_store):
    """Render research history in sidebar."""
    
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 📚 Research History")
    
    # Get recent sessions
    recent_sessions = vector_store.get_recent_sessions(limit=5)
    
    if recent_sessions:
        for session in recent_sessions:
            with st.sidebar.expander(f"📄 {session.topic[:30]}..."):
                st.write(f"**Created:** {session.created_at.strftime('%Y-%m-%d %H:%M')}")
                st.write(f"**Sources:** {len(session.sources)}")
                
                # Preview summary
                summary_preview = session.summary[:100] + "..." if len(session.summary) > 100 else session.summary
                st.write(f"**Summary:** {summary_preview}")
                
                # Load session button
                if st.button(f"Load Session", key=f"load_{session.id}"):
                    st.session_state.selected_session = session
                    st.rerun()
    else:
        st.sidebar.info("No research history yet. Start your first research!")
    
    # Search similar research
    st.sidebar.markdown("#### 🔍 Search Similar Research")
    search_query = st.sidebar.text_input(
        "Search query",
        placeholder="Enter topic to find similar research...",
        key="history_search"
    )
    
    if search_query and st.sidebar.button("Search"):
        similar_sessions = vector_store.search_similar(search_query, limit=3)
        
        if similar_sessions:
            st.sidebar.markdown("**Similar Research:**")
            for session, similarity in similar_sessions:
                with st.sidebar.expander(f"📄 {session.topic[:25]}... ({similarity:.2f})"):
                    st.write(f"**Similarity:** {similarity:.2%}")
                    st.write(f"**Created:** {session.created_at.strftime('%Y-%m-%d')}")
                    
                    if st.button(f"Load", key=f"load_similar_{session.id}"):
                        st.session_state.selected_session = session
                        st.rerun()
        else:
            st.sidebar.info("No similar research found.")

def render_system_status_sidebar(vector_store):
    """Render system status information in sidebar."""
    
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 📊 System Status")
    
    # Get vector store stats
    stats = vector_store.get_stats()
    
    if stats:
        col1, col2 = st.sidebar.columns(2)
        
        with col1:
            st.metric("Total Sessions", stats.get("total_sessions", 0))
        
        with col2:
            st.metric("Recent (7d)", stats.get("recent_sessions", 0))
        
        st.sidebar.metric(
            "With Embeddings", 
            stats.get("sessions_with_embeddings", 0)
        )
        
        # Cleanup option
        if stats.get("total_sessions", 0) > 50:
            if st.sidebar.button("🧹 Cleanup Old Sessions"):
                deleted = vector_store.cleanup_old_sessions(keep_recent=50)
                if deleted > 0:
                    st.sidebar.success(f"Deleted {deleted} old sessions")
                else:
                    st.sidebar.info("No sessions to cleanup")

def render_help_sidebar():
    """Render help and tips in sidebar."""
    
    st.sidebar.markdown("---")
    st.sidebar.markdown("### ❓ Help & Tips")
    
    with st.sidebar.expander("🚀 Quick Start"):
        st.markdown("""
        1. **Configure LLM**: Set up Ollama or LMStudio
        2. **Test Connection**: Verify LLM is working
        3. **Enter Research Topic**: Type your question
        4. **Start Research**: Click the research button
        5. **Watch Progress**: Monitor real-time updates
        """)
    
    with st.sidebar.expander("🔧 Configuration Tips"):
        st.markdown("""
        - **Research Depth**: Higher values = more thorough research
        - **Search API**: DuckDuckGo is free, others may need API keys
        - **Full Page Content**: More comprehensive but slower
        - **Embedding Model**: Smaller models are faster
        """)
    
    with st.sidebar.expander("🎯 Research Tips"):
        st.markdown("""
        - Be specific in your research topics
        - Use technical terms for better results
        - Check similar research before starting
        - Export results for future reference
        """)

# Enhanced functionality

# Enhanced functionality

# Performance and reliability improvements
