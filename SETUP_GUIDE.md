# MCP Server Setup Guide

## 🎯 What We've Built

You now have a complete **MCP (Model Context Protocol) Server** that allows AI assistants like Claude to interact with your MongoDB CRUD API using natural language!

## 📁 Files Created

1. **`mcp-server.js`** - The main MCP server that translates AI requests to API calls
2. **`test-mcp.js`** - Test script to verify everything works
3. **`simple-test.js`** - Quick connectivity test
4. **`claude_desktop_config.json`** - Configuration for Claude Desktop
5. **`MCP_README.md`** - Detailed documentation

## 🚀 Step-by-Step Setup

### Step 1: Start Your CRUD API

```bash
# In terminal 1 - Start your MongoDB CRUD API
cd d:/mongodb_crud_app
npm start
```

Keep this running! You should see:
```
MongoDB connected successfully
Server running on port 3000
```

### Step 2: Test API Connectivity

```bash
# In terminal 2 - Test the API
cd d:/mongodb_crud_app
node simple-test.js
```

Expected output:
```
Testing API...
✅ API working! Found 0 roles
Seeding database...
✅ Database seeded
✅ Found 1 users
```

### Step 3: Configure Claude Desktop

1. **Find your Claude Desktop config file:**
   - Windows: `%APPDATA%\Claude\claude_desktop_config.json`
   - Mac: `~/Library/Application Support/Claude/claude_desktop_config.json`

2. **Copy the configuration:**
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

### Step 4: Test with Claude

Once Claude Desktop restarts, you should see a 🔌 icon indicating MCP servers are connected.

Try these commands:

1. **"Show me all roles in the system"**
2. **"Create a user named Alice Johnson with email alice@test.com and admin role"**
3. **"Show me all users"**
4. **"Create a new role called 'editor' with read and write permissions"**

## 🧪 Testing Commands

### Basic User Operations
```
"Create a user named John Doe with email john@example.com, password secret123, and admin role"

"Show me all users"

"Find the user with email john@example.com"

"Update John's phone number to +1234567890"

"Delete the user with email john@example.com"
```

### Role Management
```
"Show me all available roles"

"Create a moderator role with read and write permissions"

"Update the admin role description to 'Full system administrator'"

"Delete the role with ID [role-id]"
```

### Database Operations
```
"Initialize the database with sample data"

"Seed the database"
```

## 🔧 Troubleshooting

### Issue: "Failed to retrieve users: connect ECONNREFUSED"
**Solution:** Make sure your CRUD API is running on port 3000
```bash
cd d:/mongodb_crud_app
npm start
```

### Issue: "Role 'admin' not found"
**Solution:** Seed the database first
```
Tell Claude: "Initialize the database with sample data"
```

### Issue: MCP server not connecting
**Solution:** 
1. Check Claude Desktop config file path
2. Restart Claude Desktop
3. Verify the file path in the config is correct

### Issue: "Tool execution failed"
**Solution:** Check the server logs and ensure MongoDB connection is working

## 🎉 What You Can Do Now

With your MCP server running, you can:

1. **Manage users naturally:** "Create a user for the marketing team"
2. **Handle roles easily:** "Make a content editor role"
3. **Query data intuitively:** "Show me all active users"
4. **Bulk operations:** "Create 3 test users with different roles"
5. **Complex workflows:** "Create a project manager role and assign it to Sarah"

## 🔄 Development Workflow

1. **Keep CRUD API running** in one terminal
2. **Make changes to MCP server** as needed
3. **Test with Claude Desktop** for immediate feedback
4. **Iterate and improve** based on usage

## 📈 Next Steps

Once you're comfortable with the basics:

1. **Add authentication** to the MCP server
2. **Implement search filters** (find users by role, status, etc.)
3. **Add bulk operations** (create multiple users at once)
4. **Create custom workflows** (onboarding new employees)
5. **Add data validation** and business rules
6. **Implement logging** for audit trails

## 🏗️ Architecture Overview

```
You type: "Create user John with admin role"
    ↓
Claude Desktop (interprets natural language)
    ↓
MCP Server (converts to API call)
    ↓
Your CRUD API (processes request)
    ↓
MongoDB Atlas (stores data)
    ↓
Response flows back to you
```

## 🎯 Learning Outcomes

By building this MCP server, you've learned:

1. **MCP Protocol** - How AI assistants connect to external tools
2. **API Integration** - Bridging natural language to REST APIs
3. **Error Handling** - Robust error management in distributed systems
4. **Tool Design** - Creating intuitive interfaces for AI assistants
5. **Real-world AI** - Practical AI integration beyond chatbots

Congratulations! You now have a working MCP server that demonstrates the power of connecting AI assistants to real applications! 🎉