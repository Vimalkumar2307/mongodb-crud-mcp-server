# MongoDB CRUD MCP Server

Production-ready MongoDB CRUD application with AI-powered natural language interface using the Model Context Protocol.

## Overview

This project implements the MCP (Model Context Protocol) standard for AI-tool integration. Users can perform database operations through natural language queries, powered by Groq's LLM API and a FastAPI backend.

## Key Technologies

- **FastAPI** - Async REST API with automatic OpenAPI documentation
- **Motor** - Async MongoDB driver for non-blocking database operations
- **Groq API** - Cloud-based LLM inference (llama-3.3-70b-versatile)
- **MCP Protocol** - Anthropic's standard for AI-tool communication
- **Streamlit** - Web interface for demonstrations
- **MongoDB Atlas** - Cloud database with connection pooling

## Architecture
```
User (Natural Language)
    ↓
Streamlit UI (User Interface Layer)
    ↓
MCP Server (Groq AI - Intent Extraction - Command Structuring )
    ↓
FastAPI REST API (Business Logic Layer - CRUD Operations and Validations)
    ↓
MongoDB Atlas (Data Layer) 
```

## Architecture Decisions

### Why Motor over PyMongo?
FastAPI's async architecture requires non-blocking database operations. Motor provides async/await support, enabling the server to handle 100+ concurrent requests efficiently without thread blocking.

### Why MCP Protocol?
MCP provides a standardized interface between AI assistants and tools, similar to how companies like Salesforce and GitHub expose their APIs to AI. One MCP server can integrate with multiple AI providers (Claude, ChatGPT, etc.) without custom implementations.

### Why Groq?
Eliminates local compute requirements, provides consistent sub-2-second inference, and offers production-ready infrastructure with high rate limits.

## API Documentation

Run the server and visit `http://localhost:8000/docs` for interactive Swagger documentation.

### Core Endpoints

**Users**
- `GET /api/users` - Retrieve all users with populated role data
- `POST /api/users` - Create user (auto-hashes passwords, resolves role names)
- `PUT /api/users/{id}` - Update user
- `DELETE /api/users/{id}` - Delete user

**Roles**
- `GET /api/roles` - List all roles with permissions
- `POST /api/roles` - Create role
- `PUT /api/roles/{id}` - Update role
- `DELETE /api/roles/{id}` - Delete role (validates no users assigned)

**Utility**
- `POST /api/seed` - Initialize database with default roles and admin user

## Natural Language Examples
```
"Show me all users"
"Create user with firstName Sarah and lastName Wilson as manager"
"Get all roles"
"List active users"
```

## Project Structure
```
├── api_server/          # FastAPI application
│   ├── main.py         # API endpoints and route handlers
│   ├── models.py       # Pydantic models with validation
│   └── database.py     # MongoDB connection with singleton pattern
├── mcp_server/         # MCP protocol implementation
│   └── server.py       # Tool definitions and Groq integration
├── ui/                 # Streamlit web interface
│   └── streamlit_app.py
├── requirements.txt    # Python dependencies
└── .env.example       # Configuration template
```

## Technical Highlights

- **Async patterns throughout** - All database operations use async/await for high concurrency
- **Type safety** - Pydantic models ensure data validation at API boundaries
- **Connection pooling** - Singleton pattern manages MongoDB connections efficiently
- **Index optimization** - Unique constraints and query indexes on frequently accessed fields
- **Security** - bcrypt password hashing, sensitive fields excluded from API responses

## Skills Demonstrated

- Async Python programming with FastAPI
- NoSQL database design and indexing strategies
- AI/LLM integration and prompt engineering
- Protocol implementation (MCP standard)
- Dependency management and version conflict resolution
- API design following REST principles
- Type-safe validation with Pydantic v2

## License

MIT