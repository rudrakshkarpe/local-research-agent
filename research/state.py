import operator
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from typing_extensions import Annotated
from datetime import datetime

@dataclass(kw_only=True)
class ResearchState:
    """State for the research workflow with progress tracking."""
    
    # Core research data
    research_topic: str = field(default=None)
    search_query: str = field(default=None)
    web_research_results: Annotated[List[str], operator.add] = field(default_factory=list)
    sources_gathered: Annotated[List[str], operator.add] = field(default_factory=list)
    research_loop_count: int = field(default=0)
    running_summary: str = field(default=None)
    
    # Progress tracking
    current_step: str = field(default="idle")
    step_progress: float = field(default=0.0)
    total_steps: int = field(default=5)
    step_details: Dict[str, Any] = field(default_factory=dict)
    
    # Metadata
    session_id: str = field(default=None)
    started_at: Optional[datetime] = field(default=None)
    completed_at: Optional[datetime] = field(default=None)
    error_message: Optional[str] = field(default=None)
    
    def get_progress_percentage(self) -> float:
        """Calculate overall progress percentage."""
        if self.current_step == "completed":
            return 100.0
        
        if self.current_step == "idle":
            return 0.0
        
        # Define step order and weights
        step_order = ["generate_query", "web_research", "summarize_sources", "reflect_on_summary", "finalize_summary"]
        step_weights = {
            "generate_query": 10.0,
            "web_research": 40.0,
            "summarize_sources": 25.0,
            "reflect_on_summary": 15.0,
            "finalize_summary": 10.0
        }
        
        # Calculate progress based on completed steps
        completed_progress = 0.0
        current_step_index = -1
        
        try:
            current_step_index = step_order.index(self.current_step)
        except ValueError:
            # If current step is not in the list, assume it's completed
            return 100.0
        
        # Add progress from completed steps
        for i in range(current_step_index):
            completed_progress += step_weights[step_order[i]]
        
        # Add progress from current step
        current_step_progress = step_weights.get(self.current_step, 0.0) * self.step_progress
        
        total_progress = completed_progress + current_step_progress
        
        # Factor in research loops for web research steps
        if self.current_step in ["web_research", "summarize_sources", "reflect_on_summary"]:
            # Adjust progress based on research loops
            loop_factor = min(1.0, self.research_loop_count / max(1, self.total_steps))
            if self.current_step == "web_research":
                # Scale web research progress by loop progress
                total_progress = 10.0 + (40.0 * loop_factor) + current_step_progress
        
        return min(100.0, total_progress)
    
    def update_step(self, step_name: str, progress: float = 0.0, details: Optional[Dict[str, Any]] = None):
        """Update current step and progress."""
        self.current_step = step_name
        self.step_progress = progress
        if details:
            self.step_details.update(details)
    
    def mark_completed(self):
        """Mark research as completed."""
        self.completed_at = datetime.now()
        self.current_step = "completed"
        self.step_progress = 1.0
    
    def mark_error(self, error_message: str):
        """Mark research as failed with error."""
        self.error_message = error_message
        self.current_step = "error"

@dataclass(kw_only=True)
class ResearchStateInput:
    """Input state for starting research."""
    research_topic: str = field(default=None)

@dataclass(kw_only=True)
class ResearchStateOutput:
    """Output state after research completion."""
    running_summary: str = field(default=None)
    sources_gathered: List[str] = field(default_factory=list)
    research_topic: str = field(default=None)
    session_id: str = field(default=None)

@dataclass
class ResearchSession:
    """Complete research session with metadata."""
    
    id: str
    topic: str
    summary: str
    sources: List[str]
    created_at: datetime
    completed_at: Optional[datetime] = None
    config: Optional[Dict[str, Any]] = None
    embedding: Optional[List[float]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage."""
        return {
            "id": self.id,
            "topic": self.topic,
            "summary": self.summary,
            "sources": self.sources,
            "created_at": self.created_at.isoformat(),
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "config": self.config,
            "embedding": self.embedding
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ResearchSession":
        """Create from dictionary."""
        return cls(
            id=data["id"],
            topic=data["topic"],
            summary=data["summary"],
            sources=data["sources"],
            created_at=datetime.fromisoformat(data["created_at"]),
            completed_at=datetime.fromisoformat(data["completed_at"]) if data.get("completed_at") else None,
            config=data.get("config"),
            embedding=data.get("embedding")
        )

# Step definitions for progress tracking
RESEARCH_STEPS = {
    "idle": {"name": "Ready", "description": "Waiting to start research"},
    "generate_query": {"name": "Query Generation", "description": "Generating optimized search query"},
    "web_research": {"name": "Web Research", "description": "Searching and gathering sources"},
    "summarize_sources": {"name": "Summarization", "description": "Analyzing and summarizing findings"},
    "reflect_on_summary": {"name": "Reflection", "description": "Identifying knowledge gaps"},
    "finalize_summary": {"name": "Finalization", "description": "Preparing final research report"},
    "completed": {"name": "Completed", "description": "Research completed successfully"},
    "error": {"name": "Error", "description": "Research failed with error"}
}

# Enhanced functionality

# Enhanced functionality

# Enhanced functionality

# Performance and reliability improvements
