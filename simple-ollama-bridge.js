#!/usr/bin/env node

/**
 * Simple Ollama Bridge - Direct HTTP approach
 * This bridge connects Ollama directly with your MongoDB CRUD API
 * without using MCP transport (which has compatibility issues)
 */

const readline = require('readline');
const axios = require('axios');

class SimpleOllamaBridge {
  constructor(options = {}) {
    this.ollamaUrl = options.ollamaUrl || 'http://localhost:11434';
    this.apiUrl = options.apiUrl || 'http://localhost:3000';
    this.model = options.model || 'llama3.2';
    this.conversationHistory = [];
  }

  async checkOllamaConnection() {
    try {
      const response = await axios.get(`${this.ollamaUrl}/api/tags`);
      const models = response.data.models || [];
      console.log('🦙 Ollama connected! Available models:', models.map(m => m.name).join(', '));
      
      // Check if our default model is available
      const modelExists = models.some(m => m.name.includes(this.model));
      if (!modelExists && models.length > 0) {
        this.model = models[0].name;
        console.log(`⚠️  Default model not found, using: ${this.model}`);
      }
      
      return true;
    } catch (error) {
      console.error('❌ Ollama connection failed:', error.message);
      console.log('💡 Make sure Ollama is running: ollama serve');
      return false;
    }
  }

  async checkAPIConnection() {
    try {
      const response = await axios.get(`${this.apiUrl}/api/roles`);
      console.log('✅ MongoDB API is running');
      return true;
    } catch (error) {
      console.error('❌ MongoDB API connection failed:', error.message);
      console.log('💡 Make sure your API server is running: npm start');
      return false;
    }
  }

  async processWithOllama(userInput) {
    const systemPrompt = `You are an API assistant. Your ONLY job is to convert user requests into API calls.

ALWAYS respond with JSON in this exact format:

For API requests:
{
  "action": "api_call",
  "method": "GET|POST|PUT|DELETE",
  "endpoint": "/api/endpoint",
  "data": {},
  "explanation": "what you're doing"
}

Available endpoints:
- GET /api/users (get all users)
- GET /api/users/:id (get one user)
- POST /api/users (create user - needs: firstName, lastName, email, password, role)
- PUT /api/users/:id (update user)
- DELETE /api/users/:id (delete user)
- GET /api/roles (get all roles)
- POST /api/roles (create role - needs: name, description, permissions)
- POST /api/seed (seed database)

EXAMPLES:
User: "Get all users" → {"action":"api_call","method":"GET","endpoint":"/api/users","data":{},"explanation":"Getting all users"}
User: "Show users" → {"action":"api_call","method":"GET","endpoint":"/api/users","data":{},"explanation":"Retrieving user list"}
User: "List all users" → {"action":"api_call","method":"GET","endpoint":"/api/users","data":{},"explanation":"Fetching all users"}

CRITICAL: Always make API calls. Never give explanatory responses.`;

    try {
      const response = await axios.post(`${this.ollamaUrl}/api/generate`, {
        model: this.model,
        prompt: `${systemPrompt}\n\nUser: ${userInput}\n\nAssistant:`,
        stream: false,
        options: {
          temperature: 0.1,
          top_p: 0.9
        }
      });

      const aiResponse = response.data.response;
      
      try {
        // Try to extract JSON from the response
        const jsonMatch = aiResponse.match(/\{[\s\S]*\}/);
        if (jsonMatch) {
          return JSON.parse(jsonMatch[0]);
        } else {
          // If no JSON found, return as message
          return { action: "response", message: aiResponse };
        }
      } catch (parseError) {
        return { action: "response", message: aiResponse };
      }
    } catch (error) {
      return { action: "error", message: `Ollama API error: ${error.message}` };
    }
  }

  async getRoleIdByName(roleName) {
    try {
      const response = await axios.get(`${this.apiUrl}/api/roles`);
      const roles = response.data;
      const role = roles.find(r => r.name.toLowerCase() === roleName.toLowerCase());
      return role ? role._id : null;
    } catch (error) {
      console.log(`⚠️ Could not fetch roles: ${error.message}`);
      return null;
    }
  }

  async executeAPICall(method, endpoint, data = null) {
    try {
      // Handle role name to ID conversion for user creation/update
      if (data && data.role && typeof data.role === 'string' && !data.role.match(/^[0-9a-fA-F]{24}$/)) {
        console.log(`🔍 Looking up role ID for: ${data.role}`);
        const roleId = await this.getRoleIdByName(data.role);
        if (roleId) {
          data.role = roleId;
          console.log(`✅ Found role ID: ${roleId}`);
        } else {
          throw new Error(`Role '${data.role}' not found`);
        }
      }

      let response;
      const url = `${this.apiUrl}${endpoint}`;
      
      console.log(`🔗 Making request: ${method} ${url}`);
      
      switch (method.toUpperCase()) {
        case 'GET':
          response = await axios.get(url);
          break;
        case 'POST':
          response = await axios.post(url, data);
          break;
        case 'PUT':
          response = await axios.put(url, data);
          break;
        case 'DELETE':
          response = await axios.delete(url);
          break;
        default:
          throw new Error(`Unsupported method: ${method}`);
      }

      return response.data;
    } catch (error) {
      console.log(`❌ Request failed: ${error.response?.status} ${error.response?.statusText}`);
      console.log(`❌ URL was: ${this.apiUrl}${endpoint}`);
      const errorMessage = error.response?.data?.error || error.message;
      throw new Error(errorMessage);
    }
  }

  formatUserResponse(user) {
    return `👤 User Details:
- ID: ${user._id}
- Name: ${user.firstName} ${user.lastName}
- Email: ${user.email}
- Phone: ${user.phone || 'Not provided'}
- Role: ${user.role?.name || user.role}
- Status: ${user.isActive ? 'Active' : 'Inactive'}
- Created: ${new Date(user.createdAt).toLocaleString()}`;
  }

  formatUsersResponse(users) {
    if (users.length === 0) {
      return '📝 No users found in the system.';
    }

    return `👥 Found ${users.length} user(s):\n\n` + 
      users.map((user, index) => 
        `${index + 1}. ${user.firstName} ${user.lastName} (${user.email}) - ${user.role?.name || user.role}`
      ).join('\n');
  }

  async startInteractiveSession() {
    console.log('🚀 Starting Simple Ollama Bridge...\n');

    // Check connections
    if (!await this.checkOllamaConnection()) {
      console.log('Failed to connect to Ollama. Please make sure Ollama is running.');
      return;
    }

    if (!await this.checkAPIConnection()) {
      console.log('Failed to connect to MongoDB API. Please make sure your API server is running.');
      return;
    }

    const rl = readline.createInterface({
      input: process.stdin,
      output: process.stdout,
      prompt: '🦙 Ollama > '
    });

    console.log('\n🎉 Simple Ollama Bridge Ready!');
    console.log(`💡 Powered by ${this.model} running locally`);
    console.log('\n📝 Try commands like:');
    console.log('  • "Create a new user named John Smith with email john@test.com, password 123456, and admin role"');
    console.log('  • "Show me all users in the system"');
    console.log('  • "Seed the database with default data"');
    console.log('  • "Create an admin role with all permissions"');
    console.log('  • Type "exit" to quit\n');

    rl.prompt();

    rl.on('line', async (input) => {
      const trimmedInput = input.trim();
      
      if (trimmedInput.toLowerCase() === 'exit') {
        console.log('👋 Goodbye!');
        rl.close();
        process.exit(0);
      }

      if (!trimmedInput) {
        rl.prompt();
        return;
      }

      console.log('🤔 Thinking...');

      try {
        // Process with Ollama
        const aiResponse = await this.processWithOllama(trimmedInput);

        if (aiResponse.action === 'api_call') {
          console.log(`🧠 AI Understanding: ${aiResponse.explanation}`);
          console.log(`🔧 API Call: ${aiResponse.method} ${aiResponse.endpoint}`);
          if (aiResponse.data) {
            console.log(`📋 Data:`, JSON.stringify(aiResponse.data, null, 2));
          }

          // Execute API call
          const result = await this.executeAPICall(aiResponse.method, aiResponse.endpoint, aiResponse.data);
          
          console.log('\n📊 Result:');
          
          // Format response based on endpoint
          if (aiResponse.endpoint.includes('/users') && aiResponse.method === 'GET') {
            if (Array.isArray(result)) {
              console.log(this.formatUsersResponse(result));
            } else {
              console.log(this.formatUserResponse(result));
            }
          } else if (aiResponse.endpoint.includes('/users') && aiResponse.method === 'POST') {
            console.log(`✅ User created successfully!

Details:
- Name: ${result.firstName} ${result.lastName}
- Email: ${result.email}
- Role: ${result.role?.name || result.role}
- ID: ${result._id}`);
          } else if (aiResponse.endpoint.includes('/seed')) {
            console.log(`✅ Database seeded successfully!

${result.message}

Created:
- ${result.roles?.length || 0} roles
- ${result.users?.length || 0} users

Default admin login:
- Email: admin@example.com
- Password: admin123`);
          } else {
            console.log(JSON.stringify(result, null, 2));
          }

        } else if (aiResponse.action === 'response') {
          console.log('💬 AI Response:', aiResponse.message);
        } else if (aiResponse.action === 'error') {
          console.log('❌ Error:', aiResponse.message);
        } else {
          console.log('💬 AI Response:', JSON.stringify(aiResponse, null, 2));
        }

      } catch (error) {
        console.log('❌ Error:', error.message);
      }

      console.log('\n' + '─'.repeat(50));
      rl.prompt();
    });

    rl.on('close', () => {
      console.log('\n👋 Goodbye!');
      process.exit(0);
    });
  }
}

// CLI argument parsing
const args = process.argv.slice(2);
const options = {};

for (let i = 0; i < args.length; i += 2) {
  const key = args[i];
  const value = args[i + 1];
  
  switch (key) {
    case '--model':
      options.model = value;
      break;
    case '--ollama-url':
      options.ollamaUrl = value;
      break;
    case '--api-url':
      options.apiUrl = value;
      break;
    case '--help':
      console.log(`
Simple Ollama Bridge - Direct HTTP approach

Usage: node simple-ollama-bridge.js [options]

Options:
  --model <name>        Ollama model to use (default: llama3.2)
  --ollama-url <url>    Ollama server URL (default: http://localhost:11434)
  --api-url <url>       API server URL (default: http://localhost:3000/api)
  --help               Show this help message

Examples:
  node simple-ollama-bridge.js
  node simple-ollama-bridge.js --model llama3.1
      `);
      process.exit(0);
  }
}

// Start the bridge
const bridge = new SimpleOllamaBridge(options);
bridge.startInteractiveSession().catch(console.error);