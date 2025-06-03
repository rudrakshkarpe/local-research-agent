# 🔬 Local Deep Research Agent Platform

## ✨ Features

- **Deep Research Workflow**: Multi-loop research process with query generation, web search, summarization, and reflection
- **Local LLM Integration**: Works with Ollama and LMStudio for complete privacy
- **Multiple Search APIs**: DuckDuckGo, Tavily, Perplexity, etc.
- **Real-time Progress**: Track progress in realtime step-by-step visualization
- **Smart Source Management**: Automatic deduplication and relevance scoring

### 🧠 Intelligent Features
- **Vector Embeddings**: Semantic search across research history using sentence transformers
- **Research History**: Persistent storage with similarity search
- **Configuration Management**: Easy LLM and search API configuration
- **Export Capabilities**: Download results in Markdown or text format

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Ollama or LMStudio running locally
- Git

### Installation

1. **Clone and navigate to the directory**
   ```bash
   cd streamlit-deep-researcher
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment**
   ```bash
   # Copy and edit the environment file
   cp .env.example .env
   # Edit .env with your settings
   ```

4. **Run the application**
   ```bash
   streamlit run app.py
   ```

5. **Open your browser**
   - Navigate to `http://localhost:8501`
   - Configure your LLM settings in the sidebar
   - Start researching!

## ⚙️ Configuration

### LLM Setup

#### Ollama (Recommended)
```bash
# Install Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# Pull a model
ollama pull gemma3:latest
# or
ollama pull llama3.2

# Start Ollama (usually runs automatically)
ollama serve
```

#### LMStudio
1. Download and install LMStudio
2. Load a model in LMStudio
3. Start the local server
4. Configure the base URL in the sidebar

### Environment Variables

Edit `.env` file:

```env
# LLM Settings
LOCAL_LLM="gemma3:latest"
LLM_PROVIDER="ollama"
OLLAMA_BASE_URL="http://localhost:11434/"
LMSTUDIO_BASE_URL="http://localhost:1234/v1"

# Research Settings
MAX_WEB_RESEARCH_LOOPS=3
SEARCH_API="duckduckgo"
FETCH_FULL_PAGE=true

# API Keys (optional)
TAVILY_API_KEY=""
PERPLEXITY_API_KEY=""

# Vector Embeddings
EMBEDDING_MODEL="all-MiniLM-L6-v2"
```

## 🎯 Usage Guide

### Starting Research

1. **Configure LLM**: Use the sidebar to set up your local LLM
2. **Test Connection**: Click "Test LLM Connection" to verify setup
3. **Enter Research Topic**: Type your research question in the main input
4. **Start Research**: Click "🚀 Start Research" and watch the progress
5. **View Results**: Explore the comprehensive research summary

### Research Examples

- "Latest developments in quantum computing 2024"
- "Climate change impact on agriculture"
- "Artificial intelligence safety research"
- "Renewable energy storage technologies"
- "CRISPR gene editing recent advances"

### Advanced Features

#### Research History
- **Automatic Saving**: All research sessions are saved automatically
- **Semantic Search**: Find similar research using vector embeddings
- **Session Management**: Load, view, and manage previous research

#### Configuration Options
- **Research Depth**: Adjust number of research loops (1-10)
- **Search APIs**: Choose between different search providers
- **LLM Models**: Switch between different local models
- **Embedding Models**: Select sentence transformer models

## 📊 Architecture

```
streamlit-deep-researcher/
├── app.py                          # Main Streamlit application
├── requirements.txt                # Python dependencies
├── .env                           # Configuration file
├── config/
│   ├── __init__.py
│   └── settings.py                # Configuration management
├── research/
│   ├── __init__.py
│   ├── graph.py                   # LangGraph research workflow
│   ├── state.py                   # Research state management
│   ├── utils.py                   # Search utilities
│   ├── prompts.py                 # LLM prompts
│   └── llm_providers.py           # Ollama/LMStudio integration
├── storage/
│   ├── __init__.py
│   └── vector_store.py            # Vector embeddings storage
├── components/
│   ├── __init__.py
│   ├── progress_display.py        # Progress visualization
│   └── sidebar.py                 # Configuration sidebar
└── assets/
    └── research_history.db        # SQLite database (auto-created)
```

## 🔧 Troubleshooting

### Common Issues

1. **LLM Connection Failed**
   ```bash
   # Check if Ollama is running
   ollama list
   
   # Restart Ollama
   ollama serve
   ```

2. **Module Import Errors**
   ```bash
   # Reinstall dependencies
   pip install -r requirements.txt --force-reinstall
   ```

3. **Slow Research**
   - Reduce research depth in sidebar
   - Use lighter LLM models
   - Disable "Fetch Full Page Content"

4. **Memory Issues**
   - Use smaller embedding models
   - Reduce research loops
   - Clear old research sessions

### Performance Optimization

- **Faster Models**: Use smaller LLM models like `gemma3:2b`
- **Embedding Models**: Use `all-MiniLM-L6-v2` for speed
- **Search Settings**: Disable full page content for faster searches
- **Research Depth**: Start with 2-3 loops, increase as needed

**Happy Researching! 🔬✨**

<!-- Updated documentation -->

<!-- Updated documentation -->

<!-- Updated documentation -->

<!-- Documentation enhanced -->

<!-- Documentation enhanced -->

<!-- Documentation enhanced -->

## 🚀 Recent Updates
- Enhanced research capabilities
- Improved performance and reliability
