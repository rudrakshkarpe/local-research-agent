import os
from enum import Enum
from typing import Literal, Optional
from pydantic import BaseModel, Field
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class SearchAPI(Enum):
    PERPLEXITY = "perplexity"
    TAVILY = "tavily"
    DUCKDUCKGO = "duckduckgo"
    SEARXNG = "searxng"

class LLMProvider(Enum):
    OLLAMA = "ollama"
    LMSTUDIO = "lmstudio"

class ResearchConfig(BaseModel):
    """Configuration for the research engine."""
    
    # Research Settings
    max_web_research_loops: int = Field(
        default=3,
        title="Research Depth",
        description="Number of research iterations to perform",
        ge=1,
        le=10
    )
    
    # LLM Settings
    local_llm: str = Field(
        default="gemma3:latest",
        title="LLM Model Name",
        description="Name of the LLM model to use"
    )
    
    llm_provider: Literal["ollama", "lmstudio"] = Field(
        default="ollama",
        title="LLM Provider",
        description="Provider for the LLM (Ollama or LMStudio)"
    )
    
    ollama_base_url: str = Field(
        default="http://localhost:11434/",
        title="Ollama Base URL",
        description="Base URL for Ollama API"
    )
    
    lmstudio_base_url: str = Field(
        default="http://localhost:1234/v1",
        title="LMStudio Base URL",
        description="Base URL for LMStudio OpenAI-compatible API"
    )
    
    # Search Settings
    search_api: Literal["perplexity", "tavily", "duckduckgo", "searxng"] = Field(
        default="duckduckgo",
        title="Search API",
        description="Web search API to use"
    )
    
    fetch_full_page: bool = Field(
        default=True,
        title="Fetch Full Page",
        description="Include the full page content in the search results"
    )
    
    # Processing Settings
    strip_thinking_tokens: bool = Field(
        default=True,
        title="Strip Thinking Tokens",
        description="Whether to strip <think> tokens from model responses"
    )
    
    # API Keys
    tavily_api_key: Optional[str] = Field(
        default=None,
        title="Tavily API Key",
        description="API key for Tavily search"
    )
    
    perplexity_api_key: Optional[str] = Field(
        default=None,
        title="Perplexity API Key",
        description="API key for Perplexity search"
    )
    
    searxng_url: str = Field(
        default="http://localhost:8888",
        title="SearXNG URL",
        description="URL for SearXNG instance"
    )
    
    # Vector Embeddings
    embedding_model: str = Field(
        default="all-MiniLM-L6-v2",
        title="Embedding Model",
        description="Sentence transformer model for embeddings"
    )
    
    embedding_dimension: int = Field(
        default=384,
        title="Embedding Dimension",
        description="Dimension of the embedding vectors"
    )
    
    @classmethod
    def from_env(cls) -> "ResearchConfig":
        """Create configuration from environment variables."""
        return cls(
            max_web_research_loops=int(os.getenv("MAX_WEB_RESEARCH_LOOPS", "3")),
            local_llm=os.getenv("LOCAL_LLM", "gemma3:latest"),
            llm_provider=os.getenv("LLM_PROVIDER", "ollama"),
            ollama_base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434/"),
            lmstudio_base_url=os.getenv("LMSTUDIO_BASE_URL", "http://localhost:1234/v1"),
            search_api=os.getenv("SEARCH_API", "duckduckgo"),
            fetch_full_page=os.getenv("FETCH_FULL_PAGE", "true").lower() == "true",
            strip_thinking_tokens=os.getenv("STRIP_THINKING_TOKENS", "true").lower() == "true",
            tavily_api_key=os.getenv("TAVILY_API_KEY"),
            perplexity_api_key=os.getenv("PERPLEXITY_API_KEY"),
            searxng_url=os.getenv("SEARXNG_URL", "http://localhost:8888"),
            embedding_model=os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2"),
            embedding_dimension=int(os.getenv("EMBEDDING_DIMENSION", "384"))
        )

class StreamlitConfig(BaseModel):
    """Configuration for Streamlit UI."""
    
    theme: str = Field(
        default="dark",
        title="Theme",
        description="UI theme (dark/light)"
    )
    
    research_history_limit: int = Field(
        default=100,
        title="Research History Limit",
        description="Maximum number of research sessions to keep in history"
    )
    
    @classmethod
    def from_env(cls) -> "StreamlitConfig":
        """Create configuration from environment variables."""
        return cls(
            theme=os.getenv("STREAMLIT_THEME", "dark"),
            research_history_limit=int(os.getenv("RESEARCH_HISTORY_LIMIT", "100"))
        )

# Global configuration instances
research_config = ResearchConfig.from_env()
streamlit_config = StreamlitConfig.from_env()

# Enhanced functionality

# Enhanced functionality

# Enhanced functionality

# Enhanced functionality

# Enhanced functionality

# Enhanced functionality

# Performance and reliability improvements

# Performance and reliability improvements
