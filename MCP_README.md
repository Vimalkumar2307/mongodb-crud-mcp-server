# MongoDB CRUD MCP Server

This MCP (Model Context Protocol) server allows AI assistants like Claude to interact with your MongoDB CRUD API through natural language commands.

## What You Can Do

With this MCP server, you can chat with Claude and say things like:

### User Management
- "Create a user named John Doe with email john@example.com and admin role"
- "Show me all users in the system"
- "Update the user with ID 507f1f77bcf86cd799439011 to have phone number +1234567890"
- "Delete the user with email john@example.com"
- "Find the user with ID 507f1f77bcf86cd799439011"

### Role Management
- "Create a new role called 'moderator' with read and write permissions"
- "Show me all available roles"
- "Update the admin role to include delete permissions"
- "Delete the role with ID 507f1f77bcf86cd799439012"

### Database Operations
- "Initialize the database with default data"
- "Seed the database"

## Setup Instructions

### 1. Install MCP Server Dependencies

```bash
# Install MCP server dependencies
npm install --save @modelcontextprotocol/sdk axios
```

### 2. Make MCP Server Executable

```bash
# Make the MCP server executable (Linux/Mac)
chmod +x mcp-server.js

# On Windows, you can run it directly with node
node mcp-server.js
```

### 3. Configure Claude Desktop

1. **Find your Claude Desktop config file:**
   - **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
   - **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
   - **Linux**: `~/.config/Claude/claude_desktop_config.json`

2. **Add the MCP server configuration:**
   ```json
   {
     "mcpServers": {
       "mongodb-crud": {
         "command": "node",
         "args": ["d:/mongodb_crud_app/mcp-server.js"],
         "env": {
           "NODE_ENV": "development"
         }
       }
     }
   }
   ```

3. **Restart Claude Desktop**

### 4. Start Your MongoDB CRUD API

Make sure your main CRUD API is running:

```bash
npm start
# or
npm run dev
```

The API should be running on `http://localhost:3000`

## Testing the Setup

### 1. Test Your CRUD API First

```bash
# Test if your API is working
curl http://localhost:3000/api/roles
curl http://localhost:3000/api/users
```

### 2. Test MCP Server Connection

1. Open Claude Desktop
2. Look for the 🔌 icon indicating MCP servers are connected
3. Try a simple command: "Show me all roles in the system"

### 3. Initialize Database

If you don't have any data yet:
- Say to Claude: "Initialize the database with default data"
- This will create admin and user roles, plus a default admin user

## Available Tools

The MCP server provides these tools to Claude:

| Tool | Description | Example Usage |
|------|-------------|---------------|
| `create_user` | Create a new user | "Create user Alice with email alice@test.com" |
| `get_users` | List or find users | "Show all users" or "Find user with ID xyz" |
| `update_user` | Update user details | "Update John's phone to +1234567890" |
| `delete_user` | Remove a user | "Delete user with ID xyz" |
| `create_role` | Create a new role | "Create moderator role with read, write permissions" |
| `get_roles` | List or find roles | "Show all roles" |
| `update_role` | Update role details | "Add delete permission to moderator role" |
| `delete_role` | Remove a role | "Delete role with ID xyz" |
| `seed_database` | Initialize with sample data | "Seed the database" |

## Example Conversations

### Creating Users and Roles

**You:** "Create a new role called 'editor' with read and write permissions"

**Claude:** ✅ Role created successfully!

Details:
- Name: editor
- Description: Editor role with content management access
- Permissions: read, write
- ID: 507f1f77bcf86cd799439013

**You:** "Now create a user named Sarah Connor with email sarah@skynet.com and assign her the editor role"

**Claude:** ✅ User created successfully!

Details:
- Name: Sarah Connor
- Email: sarah@skynet.com
- Role: editor
- ID: 507f1f77bcf86cd799439014

### Managing Existing Data

**You:** "Show me all users"

**Claude:** 👥 Found 2 user(s):

1. Admin User (admin@example.com) - Role: admin - Status: Active
2. Sarah Connor (sarah@skynet.com) - Role: editor - Status: Active

**You:** "Update Sarah's phone number to +1-555-0199"

**Claude:** ✅ User updated successfully!

## Troubleshooting

### Common Issues

1. **"Failed to retrieve users: connect ECONNREFUSED"**
   - Make sure your CRUD API is running on port 3000
   - Check if MongoDB connection is working

2. **"Role 'admin' not found"**
   - Run the seed command first: "Initialize the database"
   - Or create roles manually before creating users

3. **MCP server not connecting to Claude**
   - Check the config file path is correct
   - Restart Claude Desktop after config changes
   - Verify the MCP server file path in config

### Debug Mode

To see detailed logs from the MCP server:

```bash
# Run with debug output
DEBUG=* node mcp-server.js
```

## Architecture

```
User Chat → Claude Desktop → MCP Server → Your CRUD API → MongoDB Atlas
```

1. **User** types natural language command
2. **Claude** interprets the command and calls appropriate MCP tool
3. **MCP Server** converts tool call to HTTP request
4. **CRUD API** processes the request and interacts with MongoDB
5. **Response** flows back through the chain to the user

## Next Steps

Once you have the basic setup working, you can:

1. **Add more complex operations** (bulk operations, search filters)
2. **Implement authentication** for the MCP server
3. **Add data validation** and business logic
4. **Create custom prompts** for specific workflows
5. **Add logging and monitoring**

## Security Notes

- This setup is for development/learning purposes
- In production, add authentication and authorization
- Validate all inputs and sanitize data
- Use environment variables for sensitive configuration
- Consider rate limiting and access controls