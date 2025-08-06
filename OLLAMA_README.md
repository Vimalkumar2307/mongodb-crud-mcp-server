# Ollama MCP Bridge for MongoDB CRUD API

This project provides a bridge between Ollama (local LLM runner) and your MongoDB CRUD API using the Model Context Protocol (MCP). This allows you to interact with your database using natural language through a locally running AI model.

## 🚀 Quick Start

### Prerequisites

1. **Node.js** (already installed for your project)
2. **MongoDB** (your existing setup)
3. **Ollama** - Download from [ollama.ai](https://ollama.ai/download)

### Installation Steps

1. **Install Ollama**:
   ```bash
   # Windows (using winget)
   winget install Ollama.Ollama
   
   # Or download from https://ollama.ai/download
   ```

2. **Start Ollama server**:
   ```bash
   ollama serve
   ```

3. **Pull a model** (in a new terminal):
   ```bash
   # Recommended: Fast and efficient
   ollama pull llama3.2
   
   # Alternative options:
   ollama pull llama3.1    # Larger, more capable
   ollama pull codellama   # Code-focused
   ollama pull mistral     # Alternative option
   ```

4. **Verify installation**:
   ```bash
   ollama list
   ```

### Running the Bridge

1. **Start your MongoDB server** (in terminal 1):
   ```bash
   node server.js
   ```

2. **Start the Ollama MCP Bridge** (in terminal 2):
   ```bash
   node ollama-mcp-bridge.js
   ```

## 🎯 Usage Examples

Once the bridge is running, you can use natural language commands:

### User Management
```
Create a new user named Sarah with email sarah@company.com and admin role
Show me all users in the system
Update user with ID 12345 to change their email to newemail@company.com
Delete the user with email john@example.com
```

### Role Management
```
Make a manager role with read and write permissions
Create an admin role with all permissions
Show me all roles
Update the manager role to include delete permission
```

### Database Operations
```
Seed the database with default data
Show me user details for ID 67890
List all active users
```

## 🛠️ Configuration Options

### Command Line Options

```bash
# Use a different model
node ollama-mcp-bridge.js --model llama3.1

# Use a different Ollama server URL
node ollama-mcp-bridge.js --ollama-url http://localhost:11434

# Combine options
node ollama-mcp-bridge.js --model codellama --ollama-url http://localhost:11434
```

### Available Models

| Model | Size | Best For | Speed |
|-------|------|----------|-------|
| `llama3.2` | 2B | General use, fast responses | ⚡⚡⚡ |
| `llama3.1` | 8B | More complex reasoning | ⚡⚡ |
| `codellama` | 7B | Code understanding | ⚡⚡ |
| `mistral` | 7B | Alternative general model | ⚡⚡ |

## 🔧 Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   User Input    │───▶│  Ollama Bridge   │───▶│   MCP Server    │
│ (Natural Lang.) │    │  (AI Processing) │    │ (Tool Executor) │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                │                        │
                                ▼                        ▼
                       ┌─────────────────┐    ┌─────────────────┐
                       │     Ollama      │    │  MongoDB API    │
                       │ (Local LLM)     │    │   (Express)     │
                       └─────────────────┘    └─────────────────┘
```

## 🆚 Comparison: Ollama vs OpenAI

| Feature | Ollama Bridge | OpenAI Bridge |
|---------|---------------|---------------|
| **Privacy** | ✅ Fully local | ❌ Cloud-based |
| **Cost** | ✅ Free | ❌ Pay per token |
| **Speed** | ⚡ Fast (local) | ⚡ Very fast |
| **Setup** | 🔧 More setup | 🔧 Simple |
| **Models** | 🎯 Limited selection | 🎯 Latest models |
| **Offline** | ✅ Works offline | ❌ Requires internet |

## 🐛 Troubleshooting

### Common Issues

1. **"Ollama connection failed"**
   ```bash
   # Make sure Ollama is running
   ollama serve
   
   # Check if models are available
   ollama list
   ```

2. **"MCP connection failed"**
   ```bash
   # Make sure your MongoDB server is running
   node server.js
   
   # Check if MCP server file exists
   ls mcp-server.js
   ```

3. **"Model not found"**
   ```bash
   # Pull the model first
   ollama pull llama3.2
   
   # Or use a different model
   node ollama-mcp-bridge.js --model mistral
   ```

4. **Slow responses**
   - Use a smaller model: `--model llama3.2`
   - Ensure sufficient RAM (8GB+ recommended)
   - Close other resource-intensive applications

### Performance Tips

1. **Choose the right model**:
   - For quick responses: `llama3.2`
   - For better understanding: `llama3.1`
   - For code tasks: `codellama`

2. **System requirements**:
   - RAM: 8GB+ (16GB recommended)
   - Storage: 4-8GB per model
   - CPU: Modern multi-core processor

## 🔄 Switching Between Bridges

You can use both Ollama and OpenAI bridges:

```bash
# Use Ollama (local, private, free)
node ollama-mcp-bridge.js

# Use OpenAI (cloud, paid, more capable)
node openai-mcp-bridge.js  # If you create this version
```

## 📝 Available MCP Tools

The bridge provides access to these tools:

- `create_user` - Create new users
- `get_users` - Retrieve user information
- `update_user` - Update existing users
- `delete_user` - Remove users
- `create_role` - Create new roles
- `get_roles` - Retrieve role information
- `update_role` - Update existing roles
- `delete_role` - Remove roles
- `seed_database` - Initialize with default data

## 🤝 Contributing

Feel free to enhance the bridge:

1. Add support for more Ollama models
2. Improve natural language understanding
3. Add conversation memory
4. Implement batch operations
5. Add voice input/output

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

**Happy coding with local AI! 🦙✨**