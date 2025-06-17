#!/usr/bin/env node

/**
 * MCP Server for MongoDB CRUD Operations
 * This server provides tools for AI assistants to interact with the MongoDB CRUD API
 * through natural language commands.
 */

const { Server } = require('@modelcontextprotocol/sdk/server/index.js');
const { StdioServerTransport } = require('@modelcontextprotocol/sdk/server/stdio.js');
const {
  CallToolRequestSchema,
  ErrorCode,
  ListToolsRequestSchema,
  McpError,
} = require('@modelcontextprotocol/sdk/types.js');
const axios = require('axios');

// Configuration
const API_BASE_URL = 'http://localhost:3000/api';

class MongoDBCrudMCPServer {
  constructor() {
    this.server = new Server(
      {
        name: 'mongodb-crud-mcp-server',
        version: '0.1.0',
      },
      {
        capabilities: {
          tools: {},
        },
      }
    );

    this.setupToolHandlers();
    this.setupErrorHandling();
  }

  setupErrorHandling() {
    this.server.onerror = (error) => {
      console.error('[MCP Error]', error);
    };

    process.on('SIGINT', async () => {
      await this.server.close();
      process.exit(0);
    });
  }

  setupToolHandlers() {
    // List available tools
    this.server.setRequestHandler(ListToolsRequestSchema, async () => {
      return {
        tools: [
          {
            name: 'create_user',
            description: 'Create a new user in the system',
            inputSchema: {
              type: 'object',
              properties: {
                firstName: {
                  type: 'string',
                  description: 'User first name',
                },
                lastName: {
                  type: 'string',
                  description: 'User last name',
                },
                email: {
                  type: 'string',
                  description: 'User email address',
                },
                password: {
                  type: 'string',
                  description: 'User password (minimum 6 characters)',
                },
                phone: {
                  type: 'string',
                  description: 'User phone number (optional)',
                },
                dateOfBirth: {
                  type: 'string',
                  description: 'User date of birth in YYYY-MM-DD format (optional)',
                },
                role: {
                  type: 'string',
                  description: 'Role ID or role name for the user',
                },
              },
              required: ['firstName', 'lastName', 'email', 'password', 'role'],
            },
          },
          {
            name: 'get_users',
            description: 'Retrieve users from the system',
            inputSchema: {
              type: 'object',
              properties: {
                id: {
                  type: 'string',
                  description: 'Specific user ID to retrieve (optional)',
                },
              },
            },
          },
          {
            name: 'update_user',
            description: 'Update an existing user',
            inputSchema: {
              type: 'object',
              properties: {
                id: {
                  type: 'string',
                  description: 'User ID to update',
                },
                firstName: {
                  type: 'string',
                  description: 'Updated first name (optional)',
                },
                lastName: {
                  type: 'string',
                  description: 'Updated last name (optional)',
                },
                email: {
                  type: 'string',
                  description: 'Updated email address (optional)',
                },
                password: {
                  type: 'string',
                  description: 'Updated password (optional)',
                },
                phone: {
                  type: 'string',
                  description: 'Updated phone number (optional)',
                },
                dateOfBirth: {
                  type: 'string',
                  description: 'Updated date of birth in YYYY-MM-DD format (optional)',
                },
                role: {
                  type: 'string',
                  description: 'Updated role ID (optional)',
                },
                isActive: {
                  type: 'boolean',
                  description: 'Updated active status (optional)',
                },
              },
              required: ['id'],
            },
          },
          {
            name: 'delete_user',
            description: 'Delete a user from the system',
            inputSchema: {
              type: 'object',
              properties: {
                id: {
                  type: 'string',
                  description: 'User ID to delete',
                },
              },
              required: ['id'],
            },
          },
          {
            name: 'create_role',
            description: 'Create a new role in the system',
            inputSchema: {
              type: 'object',
              properties: {
                name: {
                  type: 'string',
                  description: 'Role name',
                },
                description: {
                  type: 'string',
                  description: 'Role description',
                },
                permissions: {
                  type: 'array',
                  items: {
                    type: 'string',
                    enum: ['read', 'write', 'delete', 'admin'],
                  },
                  description: 'Array of permissions for this role',
                },
                isActive: {
                  type: 'boolean',
                  description: 'Whether the role is active (default: true)',
                },
              },
              required: ['name', 'description', 'permissions'],
            },
          },
          {
            name: 'get_roles',
            description: 'Retrieve roles from the system',
            inputSchema: {
              type: 'object',
              properties: {
                id: {
                  type: 'string',
                  description: 'Specific role ID to retrieve (optional)',
                },
              },
            },
          },
          {
            name: 'update_role',
            description: 'Update an existing role',
            inputSchema: {
              type: 'object',
              properties: {
                id: {
                  type: 'string',
                  description: 'Role ID to update',
                },
                name: {
                  type: 'string',
                  description: 'Updated role name (optional)',
                },
                description: {
                  type: 'string',
                  description: 'Updated role description (optional)',
                },
                permissions: {
                  type: 'array',
                  items: {
                    type: 'string',
                    enum: ['read', 'write', 'delete', 'admin'],
                  },
                  description: 'Updated permissions array (optional)',
                },
                isActive: {
                  type: 'boolean',
                  description: 'Updated active status (optional)',
                },
              },
              required: ['id'],
            },
          },
          {
            name: 'delete_role',
            description: 'Delete a role from the system',
            inputSchema: {
              type: 'object',
              properties: {
                id: {
                  type: 'string',
                  description: 'Role ID to delete',
                },
              },
              required: ['id'],
            },
          },
          {
            name: 'seed_database',
            description: 'Initialize the database with default roles and admin user',
            inputSchema: {
              type: 'object',
              properties: {},
            },
          },
        ],
      };
    });

    // Handle tool calls
    this.server.setRequestHandler(CallToolRequestSchema, async (request) => {
      const { name, arguments: args } = request.params;

      try {
        switch (name) {
          case 'create_user':
            return await this.createUser(args);
          case 'get_users':
            return await this.getUsers(args);
          case 'update_user':
            return await this.updateUser(args);
          case 'delete_user':
            return await this.deleteUser(args);
          case 'create_role':
            return await this.createRole(args);
          case 'get_roles':
            return await this.getRoles(args);
          case 'update_role':
            return await this.updateRole(args);
          case 'delete_role':
            return await this.deleteRole(args);
          case 'seed_database':
            return await this.seedDatabase();
          default:
            throw new McpError(
              ErrorCode.MethodNotFound,
              `Unknown tool: ${name}`
            );
        }
      } catch (error) {
        if (error instanceof McpError) {
          throw error;
        }
        
        throw new McpError(
          ErrorCode.InternalError,
          `Tool execution failed: ${error.message}`
        );
      }
    });
  }

  // Helper method to resolve role name to ID
  async resolveRoleId(roleIdentifier) {
    try {
      // If it's already a valid ObjectId format, return as is
      if (/^[0-9a-fA-F]{24}$/.test(roleIdentifier)) {
        return roleIdentifier;
      }

      // Otherwise, search by name
      const response = await axios.get(`${API_BASE_URL}/roles`);
      const roles = response.data;
      const role = roles.find(r => r.name.toLowerCase() === roleIdentifier.toLowerCase());
      
      if (!role) {
        throw new Error(`Role '${roleIdentifier}' not found`);
      }
      
      return role._id;
    } catch (error) {
      throw new Error(`Failed to resolve role: ${error.message}`);
    }
  }

  // User operations
  async createUser(args) {
    try {
      // Resolve role name to ID if necessary
      const roleId = await this.resolveRoleId(args.role);
      
      const userData = {
        ...args,
        role: roleId,
      };

      const response = await axios.post(`${API_BASE_URL}/users`, userData);
      
      return {
        content: [
          {
            type: 'text',
            text: `✅ User created successfully!\n\nDetails:\n- Name: ${response.data.firstName} ${response.data.lastName}\n- Email: ${response.data.email}\n- Role: ${response.data.role.name}\n- ID: ${response.data._id}`,
          },
        ],
      };
    } catch (error) {
      const errorMessage = error.response?.data?.error || error.message;
      return {
        content: [
          {
            type: 'text',
            text: `❌ Failed to create user: ${errorMessage}`,
          },
        ],
      };
    }
  }

  async getUsers(args) {
    try {
      let response;
      
      if (args.id) {
        response = await axios.get(`${API_BASE_URL}/users/${args.id}`);
        const user = response.data;
        
        return {
          content: [
            {
              type: 'text',
              text: `👤 User Details:\n\n- ID: ${user._id}\n- Name: ${user.firstName} ${user.lastName}\n- Email: ${user.email}\n- Phone: ${user.phone || 'Not provided'}\n- Date of Birth: ${user.dateOfBirth ? new Date(user.dateOfBirth).toDateString() : 'Not provided'}\n- Role: ${user.role.name} (${user.role.description})\n- Status: ${user.isActive ? 'Active' : 'Inactive'}\n- Created: ${new Date(user.createdAt).toLocaleString()}`,
            },
          ],
        };
      } else {
        response = await axios.get(`${API_BASE_URL}/users`);
        const users = response.data;
        
        if (users.length === 0) {
          return {
            content: [
              {
                type: 'text',
                text: '📝 No users found in the system.',
              },
            ],
          };
        }

        const userList = users.map((user, index) => 
          `${index + 1}. ${user.firstName} ${user.lastName} (${user.email}) - Role: ${user.role.name} - Status: ${user.isActive ? 'Active' : 'Inactive'}`
        ).join('\n');

        return {
          content: [
            {
              type: 'text',
              text: `👥 Found ${users.length} user(s):\n\n${userList}`,
            },
          ],
        };
      }
    } catch (error) {
      const errorMessage = error.response?.data?.error || error.message;
      return {
        content: [
          {
            type: 'text',
            text: `❌ Failed to retrieve users: ${errorMessage}`,
          },
        ],
      };
    }
  }

  async updateUser(args) {
    try {
      const { id, ...updateData } = args;
      
      // Resolve role if provided
      if (updateData.role) {
        updateData.role = await this.resolveRoleId(updateData.role);
      }

      const response = await axios.put(`${API_BASE_URL}/users/${id}`, updateData);
      
      return {
        content: [
          {
            type: 'text',
            text: `✅ User updated successfully!\n\nUpdated Details:\n- Name: ${response.data.firstName} ${response.data.lastName}\n- Email: ${response.data.email}\n- Role: ${response.data.role.name}`,
          },
        ],
      };
    } catch (error) {
      const errorMessage = error.response?.data?.error || error.message;
      return {
        content: [
          {
            type: 'text',
            text: `❌ Failed to update user: ${errorMessage}`,
          },
        ],
      };
    }
  }

  async deleteUser(args) {
    try {
      await axios.delete(`${API_BASE_URL}/users/${args.id}`);
      
      return {
        content: [
          {
            type: 'text',
            text: `✅ User deleted successfully!`,
          },
        ],
      };
    } catch (error) {
      const errorMessage = error.response?.data?.error || error.message;
      return {
        content: [
          {
            type: 'text',
            text: `❌ Failed to delete user: ${errorMessage}`,
          },
        ],
      };
    }
  }

  // Role operations
  async createRole(args) {
    try {
      const response = await axios.post(`${API_BASE_URL}/roles`, args);
      
      return {
        content: [
          {
            type: 'text',
            text: `✅ Role created successfully!\n\nDetails:\n- Name: ${response.data.name}\n- Description: ${response.data.description}\n- Permissions: ${response.data.permissions.join(', ')}\n- ID: ${response.data._id}`,
          },
        ],
      };
    } catch (error) {
      const errorMessage = error.response?.data?.error || error.message;
      return {
        content: [
          {
            type: 'text',
            text: `❌ Failed to create role: ${errorMessage}`,
          },
        ],
      };
    }
  }

  async getRoles(args) {
    try {
      let response;
      
      if (args.id) {
        response = await axios.get(`${API_BASE_URL}/roles/${args.id}`);
        const role = response.data;
        
        return {
          content: [
            {
              type: 'text',
              text: `🔐 Role Details:\n\n- ID: ${role._id}\n- Name: ${role.name}\n- Description: ${role.description}\n- Permissions: ${role.permissions.join(', ')}\n- Status: ${role.isActive ? 'Active' : 'Inactive'}\n- Created: ${new Date(role.createdAt).toLocaleString()}`,
            },
          ],
        };
      } else {
        response = await axios.get(`${API_BASE_URL}/roles`);
        const roles = response.data;
        
        if (roles.length === 0) {
          return {
            content: [
              {
                type: 'text',
                text: '📝 No roles found in the system.',
              },
            ],
          };
        }

        const roleList = roles.map((role, index) => 
          `${index + 1}. ${role.name} - ${role.description} - Permissions: [${role.permissions.join(', ')}] - Status: ${role.isActive ? 'Active' : 'Inactive'}`
        ).join('\n');

        return {
          content: [
            {
              type: 'text',
              text: `🔐 Found ${roles.length} role(s):\n\n${roleList}`,
            },
          ],
        };
      }
    } catch (error) {
      const errorMessage = error.response?.data?.error || error.message;
      return {
        content: [
          {
            type: 'text',
            text: `❌ Failed to retrieve roles: ${errorMessage}`,
          },
        ],
      };
    }
  }

  async updateRole(args) {
    try {
      const { id, ...updateData } = args;
      const response = await axios.put(`${API_BASE_URL}/roles/${id}`, updateData);
      
      return {
        content: [
          {
            type: 'text',
            text: `✅ Role updated successfully!\n\nUpdated Details:\n- Name: ${response.data.name}\n- Description: ${response.data.description}\n- Permissions: ${response.data.permissions.join(', ')}`,
          },
        ],
      };
    } catch (error) {
      const errorMessage = error.response?.data?.error || error.message;
      return {
        content: [
          {
            type: 'text',
            text: `❌ Failed to update role: ${errorMessage}`,
          },
        ],
      };
    }
  }

  async deleteRole(args) {
    try {
      await axios.delete(`${API_BASE_URL}/roles/${args.id}`);
      
      return {
        content: [
          {
            type: 'text',
            text: `✅ Role deleted successfully!`,
          },
        ],
      };
    } catch (error) {
      const errorMessage = error.response?.data?.error || error.message;
      return {
        content: [
          {
            type: 'text',
            text: `❌ Failed to delete role: ${errorMessage}`,
          },
        ],
      };
    }
  }

  async seedDatabase() {
    try {
      const response = await axios.post(`${API_BASE_URL}/seed`);
      
      return {
        content: [
          {
            type: 'text',
            text: `✅ Database seeded successfully!\n\n${response.data.message}\n\nCreated:\n- ${response.data.roles.length} roles\n- ${response.data.users.length} users\n\nDefault admin login:\n- Email: admin@example.com\n- Password: admin123`,
          },
        ],
      };
    } catch (error) {
      const errorMessage = error.response?.data?.error || error.message;
      return {
        content: [
          {
            type: 'text',
            text: `❌ Failed to seed database: ${errorMessage}`,
          },
        ],
      };
    }
  }

  async run() {
    const transport = new StdioServerTransport();
    await this.server.connect(transport);
    console.error('MongoDB CRUD MCP server running on stdio');
  }
}

const server = new MongoDBCrudMCPServer();
server.run().catch(console.error);