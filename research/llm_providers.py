from typing import Optional, Dict, Any
from langchain_ollama import ChatOllama
from langchain_openai import ChatOpenAI
from config.settings import ResearchConfig

class LLMProvider:
    """Base class for LLM providers."""
    
    def __init__(self, config: ResearchConfig):
        self.config = config
        self._llm = None
        self._llm_json = None
    
    def get_llm(self, json_mode: bool = False):
        """Get LLM instance with optional JSON mode."""
        raise NotImplementedError
    
    def invoke(self, messages, json_mode: bool = False):
        """Invoke the LLM with messages."""
        llm = self.get_llm(json_mode=json_mode)
        return llm.invoke(messages)

class OllamaProvider(LLMProvider):
    """Ollama LLM provider."""
    
    def get_llm(self, json_mode: bool = False):
        """Get Ollama LLM instance."""
        if json_mode:
            if self._llm_json is None:
                self._llm_json = ChatOllama(
                    base_url=self.config.ollama_base_url,
                    model=self.config.local_llm,
                    temperature=0,
                    format="json"
                )
            return self._llm_json
        else:
            if self._llm is None:
                self._llm = ChatOllama(
                    base_url=self.config.ollama_base_url,
                    model=self.config.local_llm,
                    temperature=0
                )
            return self._llm

class LMStudioProvider(LLMProvider):
    """LMStudio LLM provider (OpenAI-compatible)."""
    
    def get_llm(self, json_mode: bool = False):
        """Get LMStudio LLM instance."""
        if json_mode:
            if self._llm_json is None:
                self._llm_json = ChatOpenAI(
                    base_url=self.config.lmstudio_base_url,
                    model=self.config.local_llm,
                    temperature=0,
                    api_key="lm-studio"  # LMStudio doesn't require real API key
                )
            return self._llm_json
        else:
            if self._llm is None:
                self._llm = ChatOpenAI(
                    base_url=self.config.lmstudio_base_url,
                    model=self.config.local_llm,
                    temperature=0,
                    api_key="lm-studio"  # LMStudio doesn't require real API key
                )
            return self._llm

def get_llm_provider(config: ResearchConfig) -> LLMProvider:
    """Get the appropriate LLM provider based on configuration."""
    if config.llm_provider == "lmstudio":
        return LMStudioProvider(config)
    else:  # Default to Ollama
        return OllamaProvider(config)

def test_llm_connection(config: ResearchConfig) -> Dict[str, Any]:
    """Test LLM connection and return status."""
    try:
        provider = get_llm_provider(config)
        
        # Test basic connection
        from langchain_core.messages import HumanMessage
        response = provider.invoke([HumanMessage(content="Hello, respond with just 'OK'")])
        
        # Test JSON mode
        json_response = provider.invoke(
            [HumanMessage(content='Respond with JSON: {"status": "ok"}')], 
            json_mode=True
        )
        
        return {
            "status": "success",
            "provider": config.llm_provider,
            "model": config.local_llm,
            "base_url": config.ollama_base_url if config.llm_provider == "ollama" else config.lmstudio_base_url,
            "basic_response": response.content[:100] if response.content else "No response",
            "json_response": json_response.content[:100] if json_response.content else "No response"
        }
    except Exception as e:
        return {
            "status": "error",
            "provider": config.llm_provider,
            "model": config.local_llm,
            "error": str(e),
            "error_type": type(e).__name__
        }

# Enhanced functionality

# Enhanced functionality

# Enhanced functionality

# Enhanced functionality

# Performance and reliability improvements
