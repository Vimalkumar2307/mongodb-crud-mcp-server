# Execution Guide - Step by Step Commands

This guide provides detailed step-by-step commands to set up, run, and use the MongoDB CRUD Application with AI Integration.

## 🚀 Prerequisites

Before starting, ensure you have:
- ✅ Node.js (v14 or higher)
- ✅ npm (comes with Node.js)
- ✅ MongoDB Atlas account
- ✅ Git (for version control)
- ✅ Ollama installed (for AI features)

## 📋 Phase 1: Initial Setup

### Step 1: Clone and Setup Project
```bash
# Navigate to your desired directory
cd d:\

# Clone the repository (if not already done)
git clone https://github.com/Vimalkumar2307/mongodb-crud-mcp-server.git mongodb_crud_app

# Navigate to project directory
cd mongodb_crud_app

# Install dependencies
npm install
```

### Step 2: Environment Configuration
```bash
# Create environment file
copy nul .env

# Edit .env file with your MongoDB connection string
# Add the following content to .env:
```

**.env file content:**
```env
MONGODB_URI=mongodb+srv://your-username:your-password@your-cluster.mongodb.net/your-database
PORT=3000
OLLAMA_API_URL=http://localhost:11434
```

### Step 3: Verify Installation
```bash
# Check if all dependencies are installed
npm list

# Verify Node.js version
node --version

# Verify npm version
npm --version
```

## 🗄️ Phase 2: Database Setup

### Step 4: MongoDB Atlas Configuration
1. **Login to MongoDB Atlas**: https://cloud.mongodb.com/
2. **Create a new cluster** (if not exists)
3. **Create database user** with read/write permissions
4. **Whitelist your IP address** (or use 0.0.0.0/0 for development)
5. **Get connection string** and update `.env` file

### Step 5: Test Database Connection
```bash
# Start the main server to test MongoDB connection
npm start

# You should see:
# "Connected to MongoDB Atlas"
# "Server running on port 3000"

# Stop the server (Ctrl+C)
```

## 🤖 Phase 3: Ollama Setup

### Step 6: Install and Configure Ollama
```bash
# Run the setup script (Windows)
setup-ollama.bat

# Or manually install Ollama:
# 1. Download from https://ollama.ai/
# 2. Install the application
# 3. Pull a model (e.g., llama2)
```

### Step 7: Verify Ollama Installation
```bash
# Check if Ollama is running
curl http://localhost:11434/api/tags

# If not running, start Ollama:
ollama serve

# Pull a model (in another terminal):
ollama pull llama2
```

## 🚀 Phase 4: Application Startup

### Step 8: Start Main Server
```bash
# Terminal 1: Start the main REST API server
npm start

# Expected output:
# "Connected to MongoDB Atlas"
# "Server running on port 3000"
# "Swagger docs available at http://localhost:3000/api-docs"
```

### Step 9: Initialize Database with Default Roles
```bash
# Open new terminal (Terminal 2)
# Create default roles using API calls

# Create admin role
curl -X POST http://localhost:3000/api/roles -H "Content-Type: application/json" -d "{\"name\":\"admin\",\"description\":\"Administrator with full access\",\"permissions\":[\"read\",\"write\",\"delete\",\"admin\"],\"isActive\":true}"

# Create user role
curl -X POST http://localhost:3000/api/roles -H "Content-Type: application/json" -d "{\"name\":\"user\",\"description\":\"Regular user with limited access\",\"permissions\":[\"read\"],\"isActive\":true}"

# Create manager role
curl -X POST http://localhost:3000/api/roles -H "Content-Type: application/json" -d "{\"name\":\"manager\",\"description\":\"Manager with moderate access\",\"permissions\":[\"read\",\"write\"],\"isActive\":true}"

# Create editor role
curl -X POST http://localhost:3000/api/roles -H "Content-Type: application/json" -d "{\"name\":\"editor\",\"description\":\"Content editor with read and write permissions\",\"permissions\":[\"read\",\"write\"],\"isActive\":true}"
```

### Step 10: Verify API Endpoints
```bash
# Test GET all roles
curl http://localhost:3000/api/roles

# Test GET all users (should be empty initially)
curl http://localhost:3000/api/users

# Access Swagger documentation
# Open browser: http://localhost:3000/api-docs
```

## 🤖 Phase 5: AI Integration

### Step 11: Start Simple Ollama Bridge
```bash
# Terminal 3: Start the simple Ollama bridge
npm run ollama-simple

# Expected output:
# "🚀 Simple Ollama Bridge running on port 3001"
# "🔗 Connected to API server at http://localhost:3000"
# "🤖 Ollama endpoint: http://localhost:11434"
```

### Step 12: Test AI Integration
```bash
# Terminal 4: Test the Ollama bridge
curl -X POST http://localhost:3001/chat -H "Content-Type: application/json" -d "{\"message\":\"Add a user named John Doe with email john@example.com as admin\"}"

# Expected response:
# {
#   "success": true,
#   "result": "✅ User created successfully! 👤 John Doe (john@example.com) - admin"
# }
```

### Step 13: Start MCP Server (Optional)
```bash
# Terminal 5: Start MCP server for AI assistants
npm run mcp

# Expected output:
# "MCP Server running on stdio"
# "Available tools: create_user, get_users, update_user, delete_user, create_role, get_roles, update_role, delete_role"
```

## 🧪 Phase 6: Testing and Validation

### Step 14: Comprehensive API Testing
```bash
# Create a test user
curl -X POST http://localhost:3000/api/users -H "Content-Type: application/json" -d "{\"firstName\":\"Test\",\"lastName\":\"User\",\"email\":\"test@example.com\",\"password\":\"password123\",\"role\":\"ROLE_ID_HERE\"}"

# Get all users
curl http://localhost:3000/api/users

# Update user
curl -X PUT http://localhost:3000/api/users/USER_ID_HERE -H "Content-Type: application/json" -d "{\"firstName\":\"Updated\",\"lastName\":\"User\"}"

# Delete user
curl -X DELETE http://localhost:3000/api/users/USER_ID_HERE
```

### Step 15: AI Command Testing
```bash
# Test various AI commands through the bridge

# Create user
curl -X POST http://localhost:3001/chat -H "Content-Type: application/json" -d "{\"message\":\"Create a user named Alice Smith with email alice@example.com as manager\"}"

# List users
curl -X POST http://localhost:3001/chat -H "Content-Type: application/json" -d "{\"message\":\"Show me all users\"}"

# Update user
curl -X POST http://localhost:3001/chat -H "Content-Type: application/json" -d "{\"message\":\"Update user Alice Smith to have admin role\"}"

# Delete user
curl -X POST http://localhost:3001/chat -H "Content-Type: application/json" -d "{\"message\":\"Delete user with email alice@example.com\"}"
```

## 🔧 Phase 7: Development Workflow

### Step 16: Development Mode
```bash
# For development with auto-restart
npm run dev

# This uses nodemon to automatically restart server on file changes
```

### Step 17: Testing Bridge Functionality
```bash
# Run bridge tests
npm run test-ollama

# This will test various scenarios and validate responses
```

## 📊 Phase 8: Monitoring and Logs

### Step 18: Monitor Application
```bash
# Check server logs (Terminal 1)
# Monitor API requests and responses

# Check bridge logs (Terminal 3)
# Monitor AI processing and API calls

# Check database operations
# Monitor MongoDB Atlas dashboard
```

### Step 19: View API Documentation
```bash
# Open browser and navigate to:
http://localhost:3000/api-docs

# This provides interactive API documentation
# You can test endpoints directly from the browser
```

## 🚀 Phase 9: Production Deployment

### Step 20: Prepare for Production
```bash
# Set production environment variables
# Update .env with production MongoDB URI
# Configure proper CORS settings
# Set up proper logging

# Build for production
npm install --production

# Start in production mode
NODE_ENV=production npm start
```

## 🔄 Phase 10: Common Operations

### Daily Development Workflow
```bash
# 1. Start all services
npm start                    # Terminal 1: Main server
npm run ollama-simple       # Terminal 2: AI bridge
ollama serve                 # Terminal 3: Ollama (if not running)

# 2. Test functionality
curl http://localhost:3000/api/users
curl -X POST http://localhost:3001/chat -H "Content-Type: application/json" -d "{\"message\":\"List all users\"}"

# 3. Make changes and test
# Files auto-reload with nodemon in dev mode

# 4. Commit changes
git add .
git commit -m "Your commit message"
git push origin main
```

### Troubleshooting Commands
```bash
# Check if ports are in use
netstat -an | findstr :3000
netstat -an | findstr :3001
netstat -an | findstr :11434

# Restart services
# Ctrl+C to stop, then restart with npm commands

# Check logs
# Look at terminal outputs for error messages

# Test individual components
curl http://localhost:3000/api/roles     # Test main server
curl http://localhost:11434/api/tags     # Test Ollama
```

## 📋 Quick Reference Commands

### Essential Commands
```bash
# Start main server
npm start

# Start development server
npm run dev

# Start AI bridge
npm run ollama-simple

# Start MCP server
npm run mcp

# Test bridge
npm run test-ollama

# Install dependencies
npm install

# Check API documentation
# Browser: http://localhost:3000/api-docs
```

### Environment Check
```bash
# Verify setup
node --version          # Should be v14+
npm --version          # Should be 6+
curl http://localhost:11434/api/tags    # Ollama running
curl http://localhost:3000/api/roles    # Server running
```

## 🎯 Success Indicators

You'll know everything is working when:
- ✅ Main server starts without errors
- ✅ MongoDB connection is established
- ✅ Swagger docs are accessible
- ✅ Ollama responds to API calls
- ✅ AI bridge processes natural language commands
- ✅ Database operations complete successfully
- ✅ All API endpoints return expected responses

## 🆘 Getting Help

If you encounter issues:
1. Check the terminal outputs for error messages
2. Verify all prerequisites are installed
3. Ensure MongoDB Atlas is properly configured
4. Confirm Ollama is running and has models installed
5. Check network connectivity and firewall settings
6. Review the CODEFLOW.md for architecture details

**Happy coding! 🚀**