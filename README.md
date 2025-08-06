# MongoDB CRUD Application with AI Integration

A comprehensive Node.js application that provides CRUD operations for MongoDB with integrated AI capabilities through Ollama and MCP (Model Context Protocol) bridges.

## 🚀 Features

- **RESTful API** - Complete CRUD operations for Users and Roles
- **MongoDB Integration** - Uses MongoDB Atlas for data persistence
- **AI Integration** - Ollama bridge for natural language database operations
- **MCP Support** - Model Context Protocol for AI assistant integration
- **API Documentation** - Swagger/OpenAPI documentation
- **Role-based Access** - User roles with permissions (admin, user, manager, editor)
- **Password Security** - Bcrypt hashing for user passwords
- **CORS Support** - Cross-origin resource sharing enabled

## 📁 Project Structure

```
mongodb_crud_app/
├── 📄 server.js                    # Main Express server with REST API
├── 📄 mcp-server.js                # MCP server for AI assistant integration
├── 📄 ollama-mcp-bridge.js         # Advanced Ollama bridge with MCP protocol
├── 📄 simple-ollama-bridge.js      # Simple Ollama bridge for direct AI interaction
├── 📄 test-ollama-bridge.js        # Test script for Ollama bridge functionality
├── 📄 setup-ollama.bat             # Windows batch script for Ollama setup
├── 📄 package.json                 # Node.js dependencies and scripts
├── 📄 .env                         # Environment variables (MongoDB URI, etc.)
├── 📄 .gitignore                   # Git ignore rules
├── 📄 LICENSE                      # MIT License
├── 📄 README.md                    # This file
├── 📄 CODEFLOW.md                  # Code architecture and flow explanation
├── 📄 EXECUTION_GUIDE.md           # Step-by-step execution commands
├── 📄 MCP_README.md                # MCP-specific documentation
├── 📄 OLLAMA_README.md             # Ollama integration documentation
└── 📄 promptlog.txt                # AI interaction logs
```

## 🛠️ Technology Stack

- **Backend**: Node.js, Express.js
- **Database**: MongoDB Atlas
- **AI Integration**: Ollama (Local LLM)
- **Protocol**: MCP (Model Context Protocol)
- **Documentation**: Swagger/OpenAPI
- **Security**: bcryptjs for password hashing
- **Development**: nodemon for hot reloading

## 📊 Database Schema

### Users Collection
```javascript
{
  firstName: String,
  lastName: String,
  email: String (unique),
  password: String (hashed),
  role: ObjectId (ref: Role),
  isActive: Boolean,
  createdAt: Date,
  updatedAt: Date
}
```

### Roles Collection
```javascript
{
  name: String (unique),
  description: String,
  permissions: [String], // ['read', 'write', 'delete', 'admin']
  isActive: Boolean,
  createdAt: Date,
  updatedAt: Date
}
```

## 🔧 Available Scripts

```bash
# Start production server
npm start

# Start development server with hot reload
npm run dev

# Start MCP server for AI assistants
npm run mcp

# Start advanced Ollama bridge
npm run ollama

# Start simple Ollama bridge
npm run ollama-simple

# Test Ollama bridge functionality
npm run test-ollama
```

## 🌐 API Endpoints

### Users API
- `GET /api/users` - Get all users
- `GET /api/users/:id` - Get user by ID
- `POST /api/users` - Create new user
- `PUT /api/users/:id` - Update user
- `DELETE /api/users/:id` - Delete user

### Roles API
- `GET /api/roles` - Get all roles
- `GET /api/roles/:id` - Get role by ID
- `POST /api/roles` - Create new role
- `PUT /api/roles/:id` - Update role
- `DELETE /api/roles/:id` - Delete role

### Documentation
- `GET /api-docs` - Swagger UI documentation
- `GET /api-docs.json` - OpenAPI JSON specification

## 🤖 AI Integration

### Ollama Bridge
The application includes two types of Ollama bridges:

1. **Simple Bridge** (`simple-ollama-bridge.js`)
   - Direct natural language to API conversion
   - Automatic role name to ObjectId lookup
   - Real-time API execution

2. **Advanced Bridge** (`ollama-mcp-bridge.js`)
   - Full MCP protocol support
   - Tool-based architecture
   - Enhanced error handling

### Example AI Commands
```
"Add a user named John Doe with email john@example.com as admin"
"List all users with manager role"
"Update user with ID 123 to have editor permissions"
"Delete the user with email test@example.com"
```

## 🔐 Environment Variables

Create a `.env` file in the root directory:

```env
MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/database
PORT=3000
OLLAMA_API_URL=http://localhost:11434
```

## 📝 Default Roles

The application comes with predefined roles:

- **admin**: Full access (read, write, delete, admin)
- **manager**: Moderate access (read, write)
- **editor**: Content access (read, write)
- **user**: Limited access (read only)

## 🚀 Quick Start

1. **Clone the repository**
2. **Install dependencies**: `npm install`
3. **Set up environment variables** in `.env`
4. **Start MongoDB Atlas** cluster
5. **Run the application**: `npm run dev`
6. **Access API documentation**: http://localhost:3000/api-docs

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

For support and questions:
- Check the [EXECUTION_GUIDE.md](EXECUTION_GUIDE.md) for step-by-step instructions
- Review [CODEFLOW.md](CODEFLOW.md) for architecture details
- Open an issue on GitHub

## 🔄 Version History

- **v1.0.0** - Initial release with CRUD operations and AI integration