# Code Flow and Architecture

This document explains the architecture, code flow, and component interactions in the MongoDB CRUD Application with AI Integration.

## 🏗️ Architecture Overview

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   AI Assistant  │    │   HTTP Client   │    │   Swagger UI    │
│   (Claude/GPT)  │    │   (Postman)     │    │   (Browser)     │
└─────────┬───────┘    └─────────┬───────┘    └─────────┬───────┘
          │                      │                      │
          │ MCP Protocol         │ REST API             │ HTTP
          │                      │                      │
┌─────────▼───────┐    ┌─────────▼──────────────────────▼───────┐
│  MCP Server     │    │           Express Server               │
│ (mcp-server.js) │    │          (server.js)                  │
└─────────────────┘    └─────────┬──────────────────────────────┘
          │                      │
          │                      │ Mongoose ODM
          │                      │
┌─────────▼───────┐    ┌─────────▼───────┐
│ Ollama Bridge   │    │   MongoDB       │
│ (AI Processing) │    │   Atlas         │
└─────────────────┘    └─────────────────┘
```

## 🔄 Component Flow

### 1. Main Server (server.js)

**Purpose**: Core REST API server with CRUD operations

**Flow**:
```
1. Initialize Express app
2. Configure middleware (CORS, JSON parsing)
3. Connect to MongoDB Atlas
4. Define Mongoose schemas (User, Role)
5. Set up Swagger documentation
6. Define REST API routes
7. Start server on specified port
```

**Key Components**:
- **Middleware Stack**: CORS → JSON Parser → Route Handlers
- **Database Models**: User and Role schemas with validation
- **API Routes**: RESTful endpoints for CRUD operations
- **Error Handling**: Centralized error responses

### 2. MCP Server (mcp-server.js)

**Purpose**: Bridge between AI assistants and the application

**Flow**:
```
1. Initialize MCP server
2. Register available tools:
   - create_user
   - get_users
   - update_user
   - delete_user
   - create_role
   - get_roles
   - update_role
   - delete_role
3. Handle tool execution requests
4. Make HTTP calls to main server
5. Return formatted responses
```

**Tool Architecture**:
```javascript
Tool Definition → Input Validation → API Call → Response Formatting
```

### 3. Simple Ollama Bridge (simple-ollama-bridge.js)

**Purpose**: Direct natural language to API conversion

**Flow**:
```
1. Start HTTP server
2. Listen for natural language requests
3. Send request to Ollama LLM
4. Parse AI response for:
   - HTTP method
   - API endpoint
   - Request data
5. Execute API call to main server
6. Return formatted result
```

**Processing Pipeline**:
```
Natural Language → Ollama LLM → JSON Parsing → API Execution → Response
```

**Special Features**:
- **Role Name Resolution**: Automatically converts role names to ObjectIds
- **Smart Parsing**: Extracts structured data from AI responses
- **Error Recovery**: Handles malformed AI responses gracefully

### 4. Advanced Ollama Bridge (ollama-mcp-bridge.js)

**Purpose**: Full MCP protocol implementation with Ollama

**Flow**:
```
1. Initialize MCP server with Ollama integration
2. Register comprehensive tool set
3. Handle complex multi-step operations
4. Provide detailed error handling
5. Support batch operations
```

## 📊 Data Flow Diagrams

### User Creation Flow
```
AI Request: "Add user John Doe as admin"
     │
     ▼
┌─────────────────┐
│ Ollama Bridge   │ ──► Parse: firstName="John", lastName="Doe", role="admin"
└─────────────────┘
     │
     ▼
┌─────────────────┐
│ Role Lookup     │ ──► Convert "admin" → ObjectId("684e698102995a6cba05d592")
└─────────────────┘
     │
     ▼
┌─────────────────┐
│ API Call        │ ──► POST /api/users with validated data
└─────────────────┘
     │
     ▼
┌─────────────────┐
│ MongoDB         │ ──► Insert document with hashed password
└─────────────────┘
     │
     ▼
┌─────────────────┐
│ Response        │ ──► Return created user with populated role
└─────────────────┘
```

### Database Query Flow
```
HTTP Request → Express Router → Mongoose Model → MongoDB Atlas → Response
```

## 🔧 Key Code Patterns

### 1. Error Handling Pattern
```javascript
try {
  // Operation
  const result = await Model.findById(id);
  if (!result) {
    return res.status(404).json({ error: 'Resource not found' });
  }
  res.json(result);
} catch (error) {
  console.error('Error:', error);
  res.status(500).json({ error: error.message });
}
```

### 2. Mongoose Schema Pattern
```javascript
const schema = new mongoose.Schema({
  // Fields with validation
  name: { type: String, required: true, unique: true },
  // References
  role: { type: mongoose.Schema.Types.ObjectId, ref: 'Role' },
  // Timestamps
}, { timestamps: true });
```

### 3. AI Response Processing Pattern
```javascript
// Parse AI response
const aiResponse = await ollama.generate(prompt);
const parsed = JSON.parse(aiResponse.response);

// Validate and execute
if (parsed.action && parsed.endpoint) {
  const result = await executeAPICall(parsed.method, parsed.endpoint, parsed.data);
  return formatResponse(result);
}
```

## 🔄 Request Lifecycle

### REST API Request
```
1. Client sends HTTP request
2. Express middleware processes request
3. Route handler validates input
4. Mongoose model interacts with MongoDB
5. Response formatted and sent back
6. Client receives JSON response
```

### AI-Powered Request
```
1. Natural language input received
2. Ollama LLM processes and understands intent
3. Bridge converts to structured API call
4. Role names resolved to ObjectIds (if needed)
5. API call executed against main server
6. Response formatted for human readability
7. Result returned to user
```

## 🧩 Component Dependencies

### Server Dependencies
```
server.js
├── express (Web framework)
├── mongoose (MongoDB ODM)
├── cors (Cross-origin support)
├── bcryptjs (Password hashing)
├── swagger-jsdoc (API documentation)
└── swagger-ui-express (Documentation UI)
```

### Bridge Dependencies
```
ollama-bridges
├── axios (HTTP client)
├── @modelcontextprotocol/sdk (MCP protocol)
└── express (HTTP server)
```

## 🔍 Code Quality Features

### 1. Input Validation
- Mongoose schema validation
- Required field checking
- Data type validation
- Unique constraint enforcement

### 2. Security Measures
- Password hashing with bcrypt
- CORS configuration
- Input sanitization
- Error message sanitization

### 3. Performance Optimizations
- Database indexing on unique fields
- Efficient query patterns
- Connection pooling
- Response caching headers

### 4. Maintainability
- Modular code structure
- Consistent error handling
- Comprehensive logging
- Clear separation of concerns

## 🚀 Scalability Considerations

### Horizontal Scaling
- Stateless server design
- External database (MongoDB Atlas)
- Load balancer ready
- Environment-based configuration

### Vertical Scaling
- Efficient memory usage
- Optimized database queries
- Minimal CPU overhead
- Configurable connection limits

## 🔧 Development Workflow

### 1. Feature Development
```
1. Define API endpoint
2. Create/update Mongoose model
3. Implement route handler
4. Add Swagger documentation
5. Update MCP tools (if needed)
6. Test with Ollama bridge
7. Write tests
8. Deploy
```

### 2. AI Integration
```
1. Define natural language patterns
2. Update Ollama prompts
3. Test AI understanding
4. Implement error handling
5. Validate API integration
6. Document usage examples
```

This architecture ensures maintainability, scalability, and seamless integration between traditional REST APIs and modern AI-powered interfaces.