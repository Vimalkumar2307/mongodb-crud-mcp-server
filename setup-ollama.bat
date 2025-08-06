@echo off
echo ========================================
echo    Ollama MCP Bridge Setup Guide
echo ========================================
echo.

echo 1. Install Ollama (if not already installed):
echo    - Download from: https://ollama.ai/download
echo    - Or use winget: winget install Ollama.Ollama
echo.

echo 2. Start Ollama service:
echo    ollama serve
echo.

echo 3. Pull a recommended model (choose one):
echo    ollama pull llama3.2          (Recommended - 2B parameters, fast)
echo    ollama pull llama3.1          (Larger model - 8B parameters)
echo    ollama pull codellama         (Code-focused model)
echo    ollama pull mistral           (Alternative option)
echo.

echo 4. Test Ollama installation:
echo    ollama list
echo.

echo 5. Start the bridge:
echo    node ollama-mcp-bridge.js
echo.

echo ========================================
echo    Quick Start Commands
echo ========================================
echo.
echo # Start Ollama server (in one terminal):
echo ollama serve
echo.
echo # Pull a model (in another terminal):
echo ollama pull llama3.2
echo.
echo # Start your MongoDB server:
echo node server.js
echo.
echo # Start the bridge (in a third terminal):
echo node ollama-mcp-bridge.js
echo.

pause