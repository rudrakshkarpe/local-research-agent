import streamlit as st
import time
from typing import Dict, Any, Optional
from research.state import ResearchState, RESEARCH_STEPS

def display_research_progress(state: ResearchState):
    """Display dynamic research progress with beautiful UI."""
    
    # Main progress bar
    progress_percentage = state.get_progress_percentage()
    st.progress(progress_percentage / 100, text=f"Research Progress: {progress_percentage:.1f}%")
    
    # Current step indicator
    current_step_info = RESEARCH_STEPS.get(state.current_step, {"name": "Unknown", "description": "Processing..."})
    
    # Step timeline
    st.markdown("### Research Timeline")
    
    # Create columns for step indicators
    steps = ["generate_query", "web_research", "summarize_sources", "reflect_on_summary", "finalize_summary"]
    cols = st.columns(len(steps))
    
    for i, step in enumerate(steps):
        with cols[i]:
            step_info = RESEARCH_STEPS[step]
            
            # Determine step status
            if state.current_step == step:
                if state.current_step == "error":
                    status_emoji = "❌"
                    status_color = "red"
                else:
                    status_emoji = "🔄"
                    status_color = "blue"
            elif steps.index(state.current_step) > i if state.current_step in steps else False:
                status_emoji = "✅"
                status_color = "green"
            elif state.current_step == "completed" and step == "finalize_summary":
                status_emoji = "✅"
                status_color = "green"
            else:
                status_emoji = "⏳"
                status_color = "gray"
            
            # Display step
            st.markdown(f"""
                <div style="text-align: center; padding: 10px; border-radius: 10px; 
                           background-color: {'#e8f5e8' if status_color == 'green' else '#e8f0ff' if status_color == 'blue' else '#ffe8e8' if status_color == 'red' else '#f5f5f5'};">
                    <div style="font-size: 24px;">{status_emoji}</div>
                    <div style="font-size: 12px; font-weight: bold; color: {status_color};">{step_info['name']}</div>
                </div>
            """, unsafe_allow_html=True)
    
    # Current step details
    if state.current_step != "idle":
        st.markdown("### Current Step")
        
        col1, col2 = st.columns([3, 1])
        with col1:
            st.markdown(f"**{current_step_info['name']}**")
            st.markdown(current_step_info['description'])
            
            # Show step details if available
            if state.step_details:
                status = state.step_details.get('status', '')
                if status:
                    st.markdown(f"*{status}*")
        
        with col2:
            # Step progress indicator
            if state.current_step not in ["completed", "error"]:
                st.markdown("**Step Progress**")
                st.progress(state.step_progress, text=f"{state.step_progress * 100:.0f}%")
    
    # Research loop indicator
    if state.research_loop_count > 0:
        st.markdown("### Research Loops")
        loop_progress = state.research_loop_count / max(1, state.total_steps)
        st.progress(loop_progress, text=f"Loop {state.research_loop_count}/{state.total_steps}")
    
    # Error display
    if state.error_message:
        st.error(f"Research Error: {state.error_message}")
    
    # Success message
    if state.current_step == "completed":
        st.success("🎉 Research completed successfully!")
        
        # Show completion stats
        if state.step_details:
            total_sources = state.step_details.get('total_sources', 0)
            summary_length = state.step_details.get('summary_length', 0)
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Sources Found", total_sources)
            with col2:
                st.metric("Summary Length", f"{summary_length:,} chars")
            with col3:
                duration = (state.completed_at - state.started_at).total_seconds() if state.completed_at and state.started_at else 0
                st.metric("Duration", f"{duration:.1f}s")

def display_step_details(state: ResearchState):
    """Display detailed information about the current step."""
    
    if not state.step_details:
        return
    
    details = state.step_details
    
    # Query generation details
    if state.current_step == "generate_query" and "query" in details:
        with st.expander("🔍 Generated Query Details", expanded=True):
            st.markdown(f"**Search Query:** `{details['query']}`")
            if "rationale" in details:
                st.markdown(f"**Rationale:** {details['rationale']}")
    
    # Web research details
    elif state.current_step == "web_research" and "sources_count" in details:
        with st.expander("🌐 Web Research Details", expanded=True):
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Sources Found", details['sources_count'])
            with col2:
                st.metric("Search API", details.get('search_api', 'Unknown'))
            
            if "query" in details:
                st.markdown(f"**Current Query:** `{details['query']}`")
    
    # Summarization details
    elif state.current_step == "summarize_sources" and "summary_length" in details:
        with st.expander("📝 Summarization Details", expanded=True):
            st.metric("Summary Length", f"{details['summary_length']:,} characters")
    
    # Reflection details
    elif state.current_step == "reflect_on_summary":
        with st.expander("🤔 Reflection Details", expanded=True):
            if "knowledge_gap" in details:
                st.markdown(f"**Knowledge Gap Identified:** {details['knowledge_gap']}")
            if "follow_up_query" in details:
                st.markdown(f"**Follow-up Query:** `{details['follow_up_query']}`")

def display_live_research_feed(state: ResearchState):
    """Display a live feed of research activities."""
    
    st.markdown("### Live Research Feed")
    
    # Create a container for live updates
    feed_container = st.container()
    
    with feed_container:
        # Show current activity
        if state.current_step != "idle":
            current_step_info = RESEARCH_STEPS.get(state.current_step, {"name": "Processing", "description": "Working..."})
            
            # Activity indicator with animation
            if state.current_step not in ["completed", "error"]:
                st.markdown(f"""
                    <div style="padding: 10px; border-left: 4px solid #1f77b4; background-color: #f0f8ff; margin: 5px 0;">
                        <strong>🔄 {current_step_info['name']}</strong><br>
                        <small>{state.step_details.get('status', current_step_info['description'])}</small>
                    </div>
                """, unsafe_allow_html=True)
            
            # Show recent activities
            activities = []
            
            # Add completed steps
            steps = ["generate_query", "web_research", "summarize_sources", "reflect_on_summary", "finalize_summary"]
            current_index = steps.index(state.current_step) if state.current_step in steps else -1
            
            for i, step in enumerate(steps):
                if i < current_index or (state.current_step == "completed" and step == "finalize_summary"):
                    step_info = RESEARCH_STEPS[step]
                    activities.append(f"✅ {step_info['name']} - Completed")
            
            # Display activities
            for activity in reversed(activities[-3:]):  # Show last 3 activities
                st.markdown(f"""
                    <div style="padding: 8px; border-left: 4px solid #28a745; background-color: #f8fff8; margin: 3px 0;">
                        <small>{activity}</small>
                    </div>
                """, unsafe_allow_html=True)

def create_animated_spinner(text: str = "Processing..."):
    """Create an animated spinner for loading states."""
    
    spinner_placeholder = st.empty()
    
    spinner_frames = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
    
    for frame in spinner_frames:
        spinner_placeholder.markdown(f"{frame} {text}")
        time.sleep(0.1)
    
    return spinner_placeholder

def display_research_metrics(state: ResearchState):
    """Display key research metrics in a dashboard format."""
    
    st.markdown("### Research Metrics")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Progress", 
            f"{state.get_progress_percentage():.1f}%",
            delta=None
        )
    
    with col2:
        st.metric(
            "Research Loops", 
            f"{state.research_loop_count}/{state.total_steps}",
            delta=None
        )
    
    with col3:
        sources_count = len(state.sources_gathered) if state.sources_gathered else 0
        st.metric(
            "Sources Gathered", 
            sources_count,
            delta=None
        )
    
    with col4:
        if state.started_at:
            if state.completed_at:
                duration = (state.completed_at - state.started_at).total_seconds()
            else:
                from datetime import datetime
                duration = (datetime.now() - state.started_at).total_seconds()
            
            st.metric(
                "Duration", 
                f"{duration:.1f}s",
                delta=None
            )
        else:
            st.metric("Duration", "0s", delta=None)

# Enhanced functionality

# Enhanced functionality

# Enhanced functionality

# Performance and reliability improvements
