"""
MCP Server for MongoDB CRUD with Groq AI Integration

This server:
1. Accepts natural language requests
2. Uses Groq LLM to understand intent
3. Calls appropriate API endpoints
4. Returns formatted responses

Interview Talking Points:
- MCP Protocol: Industry standard for AI tool integration
- Groq API: Fast inference with open-source models
- Natural language to API translation
- Error handling and validation
"""

import os
import json
import asyncio
import httpx
from typing import Any, Dict, List
from groq import Groq
from mcp.server import Server
from mcp.types import (
    Tool,
    TextContent,
    CallToolResult,
    ListToolsResult,
)
from dotenv import load_dotenv
import logging

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MCPServer:
    """
    MCP Server for MongoDB CRUD operations with AI integration.
    
    Architecture:
    - Uses Groq for natural language understanding
    - Translates NL to structured API calls
    - Handles all CRUD operations
    - Provides rich formatted responses
    """
    
    def __init__(self):
        self.server = Server("mongodb-crud-mcp")
        self.api_base_url = f"http://localhost:{os.getenv('API_PORT', '8000')}/api"
        
        # Initialize Groq client
        groq_api_key = os.getenv("GROQ_API_KEY")
        if not groq_api_key:
            raise ValueError("GROQ_API_KEY not found in environment variables")
        
        self.groq_client = Groq(api_key=groq_api_key)
        self.groq_model = os.getenv("GROQ_MODEL", "llama-3.-70b-versatile")
        
        # HTTP client for API calls
        self.http_client = httpx.AsyncClient(timeout=30.0)
        
        # Setup handlers
        self.setup_handlers()
        
        logger.info(f"✅ MCP Server initialized with Groq model: {self.groq_model}")
    
    def setup_handlers(self):
        """Register MCP protocol handlers"""
        
        @self.server.list_tools()
        async def list_tools() -> ListToolsResult:
            """
            List all available tools.
            
            This is called by AI assistants to discover capabilities.
            Each tool represents a natural language command.
            """
            return ListToolsResult(
                tools=[
                    Tool(
                        name="natural_language_query",
                        description=(
                            "Execute database operations using natural language. "
                            "Examples: 'get all users', 'create admin role', "
                            "'add user John Doe as manager', 'delete user with email test@example.com'"
                        ),
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "query": {
                                    "type": "string",
                                    "description": "Natural language query"
                                }
                            },
                            "required": ["query"]
                        }
                    ),
                    Tool(
                        name="get_users",
                        description="Get all users or a specific user by ID",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "user_id": {
                                    "type": "string",
                                    "description": "Optional user ID to get specific user"
                                }
                            }
                        }
                    ),
                    Tool(
                        name="create_user",
                        description="Create a new user",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "firstName": {"type": "string"},
                                "lastName": {"type": "string"},
                                "email": {"type": "string"},
                                "password": {"type": "string"},
                                "role": {"type": "string", "description": "Role name or ID"},
                                "phone": {"type": "string"},
                            },
                            "required": ["firstName", "lastName", "email", "password", "role"]
                        }
                    ),
                    Tool(
                        name="get_roles",
                        description="Get all roles or a specific role by ID",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "role_id": {
                                    "type": "string",
                                    "description": "Optional role ID"
                                }
                            }
                        }
                    ),
                    Tool(
                        name="create_role",
                        description="Create a new role",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "name": {"type": "string"},
                                "description": {"type": "string"},
                                "permissions": {
                                    "type": "array",
                                    "items": {"type": "string"},
                                    "description": "Array of permissions: read, write, delete, admin"
                                },
                                "is_active": {"type": "boolean"}
                            },
                            "required": ["name", "description", "permissions"]
                        }
                    ),
                ]
            )
        
        @self.server.call_tool()
        async def call_tool(name: str, arguments: Dict[str, Any]) -> CallToolResult:
            """
            Execute a tool by name.
            
            This is the main entry point for AI assistants.
            Routes requests to appropriate handlers.
            """
            try:
                if name == "natural_language_query":
                    result = await self.handle_natural_language(arguments["query"])
                elif name == "get_users":
                    result = await self.get_users(arguments.get("user_id"))
                elif name == "create_user":
                    result = await self.create_user(arguments)
                elif name == "get_roles":
                    result = await self.get_roles(arguments.get("role_id"))
                elif name == "create_role":
                    result = await self.create_role(arguments)
                else:
                    result = f"Unknown tool: {name}"
                
                return CallToolResult(content=[TextContent(type="text", text=result)])
                
            except Exception as e:
                logger.error(f"Tool execution error: {str(e)}")
                error_msg = f"❌ Error: {str(e)}"
                return CallToolResult(content=[TextContent(type="text", text=error_msg)])
    
    async def handle_natural_language(self, query: str) -> str:
        """
        Process natural language query using Groq.
        
        Steps:
        1. Send query to Groq LLM
        2. LLM returns structured JSON command
        3. Execute the command via API
        4. Format and return result
        
        Args:
            query: Natural language query from user
            
        Returns:
            Formatted response string
        """
        try:
            # Create system prompt for Groq
            system_prompt = """You are a database assistant. Convert natural language to JSON API commands.

CRITICAL RULES FOR USER CREATION:
1. When given a full name like "John Doe" or "Sarah Wilson", ALWAYS split into:
   - firstName: "John" or "Sarah"
   - lastName: "Doe" or "Wilson"
2. NEVER use a "name" field - only firstName and lastName
3. If password not provided, use: "default123"
4. If email not provided, generate: firstname.lastname@example.com
5. If role not specified, use: "user"

Available operations:
1. GET /api/users - Get all users
2. POST /api/users - Create user (needs: firstName, lastName, email, password, role)
3. GET /api/roles - Get all roles
4. POST /api/roles - Create role

Respond ONLY with valid JSON:
{
  "action": "get_users|create_user|get_roles|create_role",
  "data": {...},
  "explanation": "what you're doing"
}

EXAMPLES:
"show all users" → {"action": "get_users", "data": {}, "explanation": "Fetching all users"}
"create user John Doe" → {"action": "create_user", "data": {"firstName": "John", "lastName": "Doe", "email": "john.doe@example.com", "password": "default123", "role": "user"}, "explanation": "Creating user John Doe"}
"add Sarah Wilson as manager" → {"action": "create_user", "data": {"firstName": "Sarah", "lastName": "Wilson", "email": "sarah.wilson@example.com", "password": "default123", "role": "manager"}, "explanation": "Creating manager Sarah Wilson"}
"""

            # Call Groq API
            logger.info(f"🧠 Processing with Groq: {query}")
            
            response = self.groq_client.chat.completions.create(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": query}
                ],
                model=self.groq_model,
                temperature=0.1,
                max_tokens=500
            )
            
            ai_response = response.choices[0].message.content.strip()
            logger.info(f"🤖 Groq response: {ai_response}")
            
            # Parse JSON response
            try:
                # Extract JSON from response
                json_start = ai_response.find('{')
                json_end = ai_response.rfind('}') + 1
                if json_start != -1 and json_end > json_start:
                    json_str = ai_response[json_start:json_end]
                    command = json.loads(json_str)
                else:
                    return f"❌ Could not parse AI response: {ai_response}"
                
                # Execute the command
                action = command.get("action")
                data = command.get("data", {})
                explanation = command.get("explanation", "")
                
                logger.info(f"💭 AI Plan: {explanation}")
                logger.info(f"🔧 Executing: {action}")
                
                # Route to appropriate handler
                if action == "get_users":
                    result = await self.get_users(data.get("user_id"))
                elif action == "create_user":
                    result = await self.create_user(data)
                elif action == "get_roles":
                    result = await self.get_roles(data.get("role_id"))
                elif action == "create_role":
                    result = await self.create_role(data)
                elif action == "update_user":
                    user_id = data.pop("id", data.pop("user_id", None))
                    if not user_id:
                        return "❌ User ID required for update"
                    result = await self.update_user(user_id, data)
                elif action == "delete_user":
                    user_id = data.get("id") or data.get("user_id")
                    if not user_id:
                        return "❌ User ID required for delete"
                    result = await self.delete_user(user_id)
                else:
                    return f"❌ Unknown action: {action}"
                
                return f"💭 {explanation}\n\n{result}"
                
            except json.JSONDecodeError as e:
                logger.error(f"JSON parse error: {str(e)}")
                return f"❌ Failed to parse AI response: {ai_response}"
        
        except Exception as e:
            logger.error(f"Natural language processing error: {str(e)}")
            return f"❌ Error processing query: {str(e)}"
    
    async def get_users(self, user_id: str = None) -> str:
        """Get all users or specific user"""
        try:
            url = f"{self.api_base_url}/users"
            if user_id:
                url = f"{url}/{user_id}"
            
            response = await self.http_client.get(url)
            response.raise_for_status()
            data = response.json()
            
            if isinstance(data, list):
                if not data:
                    return "📝 No users found"
                
                result = f"👥 Found {len(data)} user(s):\n\n"
                for idx, user in enumerate(data, 1):
                    role_name = user.get('role', {}).get('name', 'N/A')
                    result += f"{idx}. {user['firstName']} {user['lastName']}\n"
                    result += f"   📧 {user['email']}\n"
                    result += f"   🔧 Role: {role_name}\n"
                    result += f"   📊 Status: {'Active' if user.get('isActive') else 'Inactive'}\n\n"
                return result
            else:
                role_name = data.get('role', {}).get('name', 'N/A')
                return f"""👤 User Details:
Name: {data['firstName']} {data['lastName']}
Email: {data['email']}
Phone: {data.get('phone', 'N/A')}
Role: {role_name}
Status: {'Active' if data.get('isActive') else 'Inactive'}
Created: {data.get('createdAt', 'N/A')}"""
        
        except httpx.HTTPStatusError as e:
            return f"❌ API Error: {e.response.text}"
        except Exception as e:
            return f"❌ Error: {str(e)}"
    
    async def create_user(self, data: Dict[str, Any]) -> str:
        """Create a new user"""
        try:
            response = await self.http_client.post(
                f"{self.api_base_url}/users",
                json=data
            )
            response.raise_for_status()
            user = response.json()
            
            role_name = user.get('role', {}).get('name', 'N/A')
            return f"""✅ User created successfully!

👤 Details:
Name: {user['firstName']} {user['lastName']}
Email: {user['email']}
Role: {role_name}
ID: {user['_id']}"""
        
        except httpx.HTTPStatusError as e:
            error_detail = e.response.json().get('detail', str(e))
            return f"❌ Failed to create user: {error_detail}"
        except Exception as e:
            return f"❌ Error: {str(e)}"
    
    async def get_roles(self, role_id: str = None) -> str:
        """Get all roles or specific role"""
        try:
            url = f"{self.api_base_url}/roles"
            if role_id:
                url = f"{url}/{role_id}"
            
            response = await self.http_client.get(url)
            response.raise_for_status()
            data = response.json()
            
            if isinstance(data, list):
                if not data:
                    return "📝 No roles found"
                
                result = f"🔧 Found {len(data)} role(s):\n\n"
                for idx, role in enumerate(data, 1):
                    perms = ', '.join(role.get('permissions', []))
                    result += f"{idx}. {role['name']}\n"
                    result += f"   📝 {role['description']}\n"
                    result += f"   🔑 Permissions: {perms}\n"
                    result += f"   📊 Status: {'Active' if role.get('is_active') else 'Inactive'}\n\n"
                return result
            else:
                perms = ', '.join(data.get('permissions', []))
                return f"""🔧 Role Details:
Name: {data['name']}
Description: {data['description']}
Permissions: {perms}
Status: {'Active' if data.get('is_active') else 'Inactive'}"""
        
        except httpx.HTTPStatusError as e:
            return f"❌ API Error: {e.response.text}"
        except Exception as e:
            return f"❌ Error: {str(e)}"
    
    async def create_role(self, data: Dict[str, Any]) -> str:
        """Create a new role"""
        try:
            response = await self.http_client.post(
                f"{self.api_base_url}/roles",
                json=data
            )
            response.raise_for_status()
            role = response.json()
            
            perms = ', '.join(role.get('permissions', []))
            return f"""✅ Role created successfully!

🔧 Details:
Name: {role['name']}
Description: {role['description']}
Permissions: {perms}
ID: {role['_id']}"""
        
        except httpx.HTTPStatusError as e:
            error_detail = e.response.json().get('detail', str(e))
            return f"❌ Failed to create role: {error_detail}"
        except Exception as e:
            return f"❌ Error: {str(e)}"
    
    async def update_user(self, user_id: str, data: Dict[str, Any]) -> str:
        """Update a user"""
        try:
            response = await self.http_client.put(
                f"{self.api_base_url}/users/{user_id}",
                json=data
            )
            response.raise_for_status()
            user = response.json()
            
            return f"✅ User updated successfully!\nName: {user['firstName']} {user['lastName']}"
        
        except httpx.HTTPStatusError as e:
            return f"❌ Update failed: {e.response.text}"
        except Exception as e:
            return f"❌ Error: {str(e)}"
    
    async def delete_user(self, user_id: str) -> str:
        """Delete a user"""
        try:
            response = await self.http_client.delete(
                f"{self.api_base_url}/users/{user_id}"
            )
            response.raise_for_status()
            return "✅ User deleted successfully!"
        
        except httpx.HTTPStatusError as e:
            return f"❌ Delete failed: {e.response.text}"
        except Exception as e:
            return f"❌ Error: {str(e)}"
    
    async def run(self):
        """Run the MCP server"""
        from mcp.server.stdio import stdio_server
        
        async with stdio_server() as (read_stream, write_stream):
            logger.info("🚀 MCP Server running...")
            await self.server.run(
                read_stream,
                write_stream,
                self.server.create_initialization_options()
            )
    
    async def cleanup(self):
        """Cleanup resources"""
        await self.http_client.aclose()


# Entry point
if __name__ == "__main__":
    server = MCPServer()
    try:
        asyncio.run(server.run())
    except KeyboardInterrupt:
        logger.info("\n👋 Shutting down MCP Server...")
    finally:
        asyncio.run(server.cleanup())
