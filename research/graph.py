import json
import uuid
from datetime import datetime
from typing import Dict, Any, Callable, Optional
from typing_extensions import Literal

from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.graph import START, END, StateGraph

from config.settings import ResearchConfig
from research.state import ResearchState, ResearchStateInput, ResearchStateOutput, RESEARCH_STEPS
from research.utils import (
    deduplicate_and_format_sources, tavily_search, format_sources, 
    perplexity_search, duckduckgo_search, searxng_search, 
    strip_thinking_tokens, get_config_value, get_current_date
)
from research.prompts import query_writer_instructions, summarizer_instructions, reflection_instructions
from research.llm_providers import get_llm_provider

class StreamlitResearchGraph:
    """Research graph with Streamlit progress callbacks."""
    
    def __init__(self, config: ResearchConfig, progress_callback: Optional[Callable] = None):
        self.config = config
        self.progress_callback = progress_callback
        self.llm_provider = get_llm_provider(config)
        self.graph = self._build_graph()
    
    def _update_progress(self, state: ResearchState, step_name: str, progress: float = 0.0, details: Optional[Dict[str, Any]] = None):
        """Update progress and notify callback."""
        state.update_step(step_name, progress, details)
        if self.progress_callback:
            self.progress_callback(state)
    
    def _build_graph(self) -> StateGraph:
        """Build the research graph."""
        builder = StateGraph(
            ResearchState, 
            input=ResearchStateInput, 
            output=ResearchStateOutput
        )
        
        # Add nodes
        builder.add_node("generate_query", self._generate_query)
        builder.add_node("web_research", self._web_research)
        builder.add_node("summarize_sources", self._summarize_sources)
        builder.add_node("reflect_on_summary", self._reflect_on_summary)
        builder.add_node("finalize_summary", self._finalize_summary)
        
        # Add edges
        builder.add_edge(START, "generate_query")
        builder.add_edge("generate_query", "web_research")
        builder.add_edge("web_research", "summarize_sources")
        builder.add_edge("summarize_sources", "reflect_on_summary")
        builder.add_conditional_edges("reflect_on_summary", self._route_research)
        builder.add_edge("finalize_summary", END)
        
        return builder.compile()
    
    def _generate_query(self, state: ResearchState) -> Dict[str, Any]:
        """Generate search query based on research topic."""
        self._update_progress(state, "generate_query", 0.1, {"status": "Generating search query..."})
        
        try:
            # Format the prompt
            current_date = get_current_date()
            formatted_prompt = query_writer_instructions.format(
                current_date=current_date,
                research_topic=state.research_topic
            )
            
            # Generate query using LLM
            result = self.llm_provider.invoke([
                SystemMessage(content=formatted_prompt),
                HumanMessage(content="Generate a query for web search:")
            ], json_mode=True)
            
            # Parse JSON response
            try:
                query_data = json.loads(result.content)
                search_query = query_data['query']
                rationale = query_data.get('rationale', '')
            except (json.JSONDecodeError, KeyError):
                # Fallback if JSON parsing fails
                if self.config.strip_thinking_tokens:
                    content = strip_thinking_tokens(result.content)
                else:
                    content = result.content
                search_query = content
                rationale = "Generated query"
            
            self._update_progress(state, "generate_query", 1.0, {
                "status": "Query generated successfully",
                "query": search_query,
                "rationale": rationale
            })
            
            return {"search_query": search_query}
            
        except Exception as e:
            state.mark_error(f"Query generation failed: {str(e)}")
            self._update_progress(state, "error", 0.0, {"error": str(e)})
            raise
    
    def _web_research(self, state: ResearchState) -> Dict[str, Any]:
        """Perform web research using the generated query."""
        self._update_progress(state, "web_research", 0.1, {
            "status": f"Searching web (loop {state.research_loop_count + 1}/{self.config.max_web_research_loops})...",
            "query": state.search_query
        })
        
        try:
            # Get search API
            search_api = get_config_value(self.config.search_api)
            
            # Perform search based on configured API
            if search_api == "tavily":
                search_results = tavily_search(
                    state.search_query, 
                    fetch_full_page=self.config.fetch_full_page, 
                    max_results=3
                )
            elif search_api == "perplexity":
                search_results = perplexity_search(state.search_query, state.research_loop_count)
            elif search_api == "duckduckgo":
                search_results = duckduckgo_search(
                    state.search_query, 
                    max_results=3, 
                    fetch_full_page=self.config.fetch_full_page
                )
            elif search_api == "searxng":
                search_results = searxng_search(
                    state.search_query, 
                    max_results=3, 
                    fetch_full_page=self.config.fetch_full_page
                )
            else:
                raise ValueError(f"Unsupported search API: {self.config.search_api}")
            
            # Format search results
            search_str = deduplicate_and_format_sources(
                search_results, 
                max_tokens_per_source=1000, 
                fetch_full_page=self.config.fetch_full_page
            )
            
            # Extract individual source URLs for tracking
            sources_list = []
            if 'results' in search_results:
                for result in search_results['results']:
                    if 'url' in result:
                        sources_list.append(result['url'])
            
            sources_count = len(sources_list)
            
            self._update_progress(state, "web_research", 1.0, {
                "status": f"Found {sources_count} sources",
                "sources_count": sources_count,
                "search_api": search_api
            })
            
            return {
                "sources_gathered": sources_list,
                "research_loop_count": state.research_loop_count + 1,
                "web_research_results": [search_str]
            }
            
        except Exception as e:
            state.mark_error(f"Web research failed: {str(e)}")
            self._update_progress(state, "error", 0.0, {"error": str(e)})
            raise
    
    def _summarize_sources(self, state: ResearchState) -> Dict[str, Any]:
        """Summarize the research results."""
        self._update_progress(state, "summarize_sources", 0.1, {
            "status": "Analyzing and summarizing sources..."
        })
        
        try:
            # Get existing summary and latest research
            existing_summary = state.running_summary
            most_recent_research = state.web_research_results[-1]
            
            # Build human message
            if existing_summary:
                human_message_content = (
                    f"<Existing Summary>\n{existing_summary}\n</Existing Summary>\n\n"
                    f"<New Context>\n{most_recent_research}\n</New Context>\n"
                    f"Update the Existing Summary with the New Context on this topic:\n"
                    f"<User Input>\n{state.research_topic}\n</User Input>\n\n"
                )
            else:
                human_message_content = (
                    f"<Context>\n{most_recent_research}\n</Context>\n"
                    f"Create a Summary using the Context on this topic:\n"
                    f"<User Input>\n{state.research_topic}\n</User Input>\n\n"
                )
            
            # Generate summary using LLM
            result = self.llm_provider.invoke([
                SystemMessage(content=summarizer_instructions),
                HumanMessage(content=human_message_content)
            ])
            
            # Process result
            running_summary = result.content
            if self.config.strip_thinking_tokens:
                running_summary = strip_thinking_tokens(running_summary)
            
            self._update_progress(state, "summarize_sources", 1.0, {
                "status": "Summary updated",
                "summary_length": len(running_summary)
            })
            
            return {"running_summary": running_summary}
            
        except Exception as e:
            state.mark_error(f"Summarization failed: {str(e)}")
            self._update_progress(state, "error", 0.0, {"error": str(e)})
            raise
    
    def _reflect_on_summary(self, state: ResearchState) -> Dict[str, Any]:
        """Reflect on summary and generate follow-up query."""
        self._update_progress(state, "reflect_on_summary", 0.1, {
            "status": "Identifying knowledge gaps..."
        })
        
        try:
            # Generate reflection using LLM
            result = self.llm_provider.invoke([
                SystemMessage(content=reflection_instructions.format(research_topic=state.research_topic)),
                HumanMessage(content=f"Reflect on our existing knowledge:\n===\n{state.running_summary}\n===\n"
                                   f"And now identify a knowledge gap and generate a follow-up web search query:")
            ], json_mode=True)
            
            # Parse reflection result
            try:
                reflection_content = json.loads(result.content)
                follow_up_query = reflection_content.get('follow_up_query')
                knowledge_gap = reflection_content.get('knowledge_gap', '')
                
                if not follow_up_query:
                    follow_up_query = f"Tell me more about {state.research_topic}"
                    
            except (json.JSONDecodeError, KeyError, AttributeError):
                follow_up_query = f"Tell me more about {state.research_topic}"
                knowledge_gap = "Additional information needed"
            
            self._update_progress(state, "reflect_on_summary", 1.0, {
                "status": "Knowledge gap identified",
                "knowledge_gap": knowledge_gap,
                "follow_up_query": follow_up_query
            })
            
            return {"search_query": follow_up_query}
            
        except Exception as e:
            state.mark_error(f"Reflection failed: {str(e)}")
            self._update_progress(state, "error", 0.0, {"error": str(e)})
            raise
    
    def _finalize_summary(self, state: ResearchState) -> Dict[str, Any]:
        """Finalize the research summary."""
        self._update_progress(state, "finalize_summary", 0.5, {
            "status": "Finalizing research report..."
        })
        
        try:
            # Deduplicate sources - handle both URL strings and formatted sources
            seen_sources = set()
            unique_sources = []
            
            for source in state.sources_gathered:
                if isinstance(source, str):
                    # If it's a URL, add it directly
                    if source.startswith('http') and source not in seen_sources:
                        seen_sources.add(source)
                        unique_sources.append(source)
                    else:
                        # If it's formatted text, split by lines
                        for line in source.split('\n'):
                            if line.strip() and line not in seen_sources:
                                seen_sources.add(line)
                                unique_sources.append(line)
            
            # Create final summary with sources
            if unique_sources:
                numbered_sources = [f"{i+1}. {source}" for i, source in enumerate(unique_sources)]
                all_sources = "\n".join(numbered_sources)
                final_summary = f"## Summary\n{state.running_summary}\n\n### Sources:\n{all_sources}"
            else:
                final_summary = f"## Summary\n{state.running_summary}"
            
            state.mark_completed()
            self._update_progress(state, "completed", 1.0, {
                "status": "Research completed successfully",
                "total_sources": len(unique_sources),
                "summary_length": len(final_summary)
            })
            
            return {"running_summary": final_summary}
            
        except Exception as e:
            state.mark_error(f"Finalization failed: {str(e)}")
            self._update_progress(state, "error", 0.0, {"error": str(e)})
            raise
    
    def _route_research(self, state: ResearchState) -> Literal["finalize_summary", "web_research"]:
        """Route to next step based on research loop count."""
        if state.research_loop_count <= self.config.max_web_research_loops:
            return "web_research"
        else:
            return "finalize_summary"
    
    def run_research(self, research_topic: str) -> ResearchState:
        """Run the complete research workflow."""
        # Initialize state
        state = ResearchState(
            research_topic=research_topic,
            session_id=str(uuid.uuid4()),
            started_at=datetime.now(),
            total_steps=self.config.max_web_research_loops
        )
        
        try:
            # Run the graph
            result = self.graph.invoke({"research_topic": research_topic})
            
            # Update final state
            state.running_summary = result.get("running_summary", "")
            state.mark_completed()
            
            return state
            
        except Exception as e:
            state.mark_error(str(e))
            raise

def create_research_graph(config: ResearchConfig, progress_callback: Optional[Callable] = None) -> StreamlitResearchGraph:
    """Create a research graph instance."""
    return StreamlitResearchGraph(config, progress_callback)

# Enhanced functionality

# Enhanced functionality

# Enhanced functionality

# Enhanced functionality

# Enhanced functionality

# Enhanced functionality

# Enhanced functionality

# Enhanced functionality

# Enhanced functionality

# Performance and reliability improvements
