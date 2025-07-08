#!/usr/bin/env python3
"""
Startup script for the Streamlit Deep Research Platform.
This script provides a simple way to launch the application with proper configuration.
"""

import os
import sys
import subprocess
from pathlib import Path

def check_dependencies():
    """Check if all required dependencies are installed."""
    try:
        import streamlit
        import langchain_ollama
        import sentence_transformers
        import duckduckgo_search
        print("✅ All dependencies are installed")
        return True
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("Please run: pip install -r requirements.txt")
        return False

def check_environment():
    """Check if environment is properly configured."""
    env_file = Path(".env")
    if not env_file.exists():
        print("⚠️  .env file not found. Using default configuration.")
        print("You can create a .env file to customize settings.")
    else:
        print("✅ Environment file found")
    
    return True

def main():
    """Main function to start the Streamlit application."""
    print("🔬 Starting Streamlit Deep Research Platform...")
    print("=" * 50)
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    # Check environment
    if not check_environment():
        sys.exit(1)
    
    # Set Streamlit configuration
    os.environ.setdefault("STREAMLIT_SERVER_PORT", "8501")
    os.environ.setdefault("STREAMLIT_SERVER_ADDRESS", "localhost")
    
    print("\n🚀 Launching Streamlit application...")
    print("📱 Open your browser and navigate to: http://localhost:8501")
    print("🛑 Press Ctrl+C to stop the application")
    print("=" * 50)
    
    try:
        # Launch Streamlit
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", "app.py",
            "--server.port", "8501",
            "--server.address", "localhost",
            "--browser.gatherUsageStats", "false"
        ], check=True)
    except KeyboardInterrupt:
        print("\n\n🛑 Application stopped by user")
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Error starting application: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

# Enhanced functionality

# Performance and reliability improvements
