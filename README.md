# 🔬 Local Deep Research Agent Platform

<div align="center">

**A powerful local research platform with AI-driven deep research capabilities**

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://python.org)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-red.svg)](https://streamlit.io)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

</div>

<details>
<summary><strong>✨ Features</strong></summary>

### 🔍 Core Research Capabilities
- **Deep Research Workflow**: Multi-loop research process with query generation, web search, summarization, and reflection
- **Local LLM Integration**: Works with Ollama and LMStudio for complete privacy
- **Multiple Search APIs**: DuckDuckGo, Tavily, Perplexity, etc.
- **Real-time Progress**: Track progress in realtime step-by-step visualization
- **Smart Source Management**: Automatic deduplication and relevance scoring
- **Vector Embeddings**: Semantic search across research history using sentence transformers
- **Research History**: Persistent storage with similarity search
- **Configuration Management**: Easy LLM and search API configuration
- **Export Capabilities**: Download results in Markdown or text format

</details>



<details>
<summary><strong>🚀 Quick Start</strong></summary>

### 📋 Prerequisites

| Requirement | Version | Description |
|-------------|---------|-------------|
| 🐍 Python | 3.11+ | Core runtime environment |
| 🦙 Ollama/LMStudio | Latest | Local LLM provider |
| 📦 Git | Latest | Version control |

### 🛠️ Installation Steps

```bash
# 1. Clone and navigate to the directory
cd streamlit-deep-researcher

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure environment
cp .env.example .env
# Edit .env with your settings

# 4. Run the application
streamlit run app.py

# 5. Open your browser at http://localhost:8501
```

### 🎯 First Steps
1. Navigate to `http://localhost:8501`
2. Configure your LLM settings in the sidebar
3. Start researching!

</details>



<details>
<summary><strong>⚙️ Configuration</strong></summary>

### 🦙 LLM Setup

<details>
<summary><strong>Ollama (Recommended)</strong></summary>

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

</details>

<details>
<summary><strong>LMStudio</strong></summary>

1. Download and install LMStudio
2. Load a model in LMStudio
3. Start the local server
4. Configure the base URL in the sidebar

</details>

### 🔧 Environment Variables

<details>
<summary><strong>Configuration File (.env)</strong></summary>

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

</details>

</details>



<details>
<summary><strong>🎯 Usage Guide</strong></summary>

### 🚀 Starting Research

| Step | Action | Description |
|------|--------|-------------|
| 1️⃣ | **Configure LLM** | Use the sidebar to set up your local LLM |
| 2️⃣ | **Test Connection** | Click "Test LLM Connection" to verify setup |
| 3️⃣ | **Enter Research Topic** | Type your research question in the main input |
| 4️⃣ | **Start Research** | Click "🚀 Start Research" and watch the progress |
| 5️⃣ | **View Results** | Explore the comprehensive research summary |

### 💡 Research Examples

<details>
<summary><strong>Sample Research Topics</strong></summary>

- 🔬 "Latest developments in quantum computing 2024"
- 🌱 "Climate change impact on agriculture"
- 🤖 "Artificial intelligence safety research"
- ⚡ "Renewable energy storage technologies"
- 🧬 "CRISPR gene editing recent advances"

</details>

### 🔧 Advanced Features

<details>
<summary><strong>Research History</strong></summary>

- **Automatic Saving**: All research sessions are saved automatically
- **Semantic Search**: Find similar research using vector embeddings
- **Session Management**: Load, view, and manage previous research

</details>

<details>
<summary><strong>Configuration Options</strong></summary>

- **Research Depth**: Adjust number of research loops (1-10)
- **Search APIs**: Choose between different search providers
- **LLM Models**: Switch between different local models
- **Embedding Models**: Select sentence transformer models

</details>

</details>


<details>
<summary><strong>📊 Architecture</strong></summary>

### 📁 Project Structure

```
streamlit-deep-researcher/
├── 📱 app.py                          # Main Streamlit application
├── 📋 requirements.txt                # Python dependencies
├── ⚙️ .env                           # Configuration file
├── 📂 config/
│   ├── __init__.py
│   └── ⚙️ settings.py                # Configuration management
├── 📂 research/
│   ├── __init__.py
│   ├── 🔄 graph.py                   # LangGraph research workflow
│   ├── 📊 state.py                   # Research state management
│   ├── 🔍 utils.py                   # Search utilities
│   ├── 💬 prompts.py                 # LLM prompts
│   └── 🤖 llm_providers.py           # Ollama/LMStudio integration
├── 📂 storage/
│   ├── __init__.py
│   └── 🗄️ vector_store.py            # Vector embeddings storage
├── 📂 components/
│   ├── __init__.py
│   ├── 📈 progress_display.py        # Progress visualization
│   └── 🎛️ sidebar.py                 # Configuration sidebar
└── 📂 assets/
    └── 🗃️ research_history.db        # SQLite database (auto-created)
```

### 🏗️ System Components

| Component | Purpose | Technology |
|-----------|---------|------------|
| **Frontend** | User interface | Streamlit |
| **Research Engine** | Core logic | LangGraph |
| **LLM Integration** | AI processing | Ollama/LMStudio |
| **Vector Store** | Embeddings | Sentence Transformers |
| **Search APIs** | Web research | Multiple providers |

</details>


<details>
<summary><strong>🔧 Troubleshooting</strong></summary>

### ❗ Common Issues

<details>
<summary><strong>🔌 LLM Connection Failed</strong></summary>

```bash
# Check if Ollama is running
ollama list

# Restart Ollama
ollama serve
```

**Solution**: Ensure Ollama service is running and accessible on the configured port.

</details>

<details>
<summary><strong>📦 Module Import Errors</strong></summary>

```bash
# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

**Solution**: Clean reinstall of all Python dependencies.

</details>

<details>
<summary><strong>🐌 Slow Research Performance</strong></summary>

**Quick Fixes**:
- Reduce research depth in sidebar
- Use lighter LLM models
- Disable "Fetch Full Page Content"

</details>

<details>
<summary><strong>💾 Memory Issues</strong></summary>

**Optimization Steps**:
- Use smaller embedding models
- Reduce research loops
- Clear old research sessions

</details>

### ⚡ Performance Optimization

| Optimization | Recommendation | Impact |
|--------------|----------------|---------|
| **Model Size** | Use `gemma3:2b` instead of larger models | 🚀 Faster |
| **Embeddings** | Use `all-MiniLM-L6-v2` | 🚀 Faster |
| **Search Settings** | Disable full page content | 🚀 Faster |
| **Research Depth** | Start with 2-3 loops | ⚖️ Balanced |

</details>



<details>
<summary><strong>🚀 Recent Updates</strong></summary>

### ✨ Latest Enhancements
- 🔧 Enhanced research capabilities
- ⚡ Improved performance and reliability
- 🎨 Better user interface design
- 🔍 Advanced search functionality

### 📈 Performance Improvements
- Faster LLM response times
- Optimized vector embeddings
- Reduced memory usage
- Better error handling

</details>



<div align="center">

**Happy Researching! 🔬✨**

</div>
