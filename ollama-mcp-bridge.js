#!/usr/bin/env node

/**
 * Ollama MCP Bridge
 * This bridge connects Ollama (local LLM) with your MongoDB CRUD MCP server
 * allowing natural language interaction with your database through a local AI model.
 */

const { Client } = require('@modelcontextprotocol/sdk/client/index.js');
const { StdioClientTransport } = require('@modelcontextprotocol/sdk/client/stdio.js');
const { spawn } = require('child_process');
const readline = require('readline');
const axios = require('axios');

class OllamaMCPBridge {
  constructor(options = {}) {
    this.ollamaUrl = options.ollamaUrl || 'http://localhost:11434';
    this.model = options.model || 'llama3.2'; // Default model, can be changed
    this.client = new Client({
      name: "ollama-mcp-bridge",
      version: "1.0.0"
    }, {
      capabilities: {}
    });
    this.availableTools = [];
    this.conversationHistory = [];
  }

  async connectToMCP() {
    try {
      console.log('🔌 Starting MCP server...');
      const serverProcess = spawn('node', ['mcp-server.js'], {
        stdio: ['pipe', 'pipe', 'inherit'],
        cwd: __dirname
      });

      // Wait a moment for the server to start
      await new Promise(resolve => setTimeout(resolve, 1000));

      const transport = new StdioClientTransport({
        readable: serverProcess.stdout,
        writable: serverProcess.stdin
      });

      await this.client.connect(transport);
      console.log('✅ Connected to MCP server!');

      const tools = await this.client.listTools();
      this.availableTools = tools.tools;
      console.log('🛠️  Available tools:', this.availableTools.map(t => t.name).join(', '));
      
      return true;
    } catch (error) {
      console.error('❌ MCP connection failed:', error.message);
      return false;
    }
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

  async processWithOllama(userInput) {
    const systemPrompt = `You are an AI assistant that helps users interact with a MongoDB CRUD API through natural language.

Available MCP tools:
${this.availableTools.map(tool => `- ${tool.name}: ${tool.description}\n  Schema: ${JSON.stringify(tool.inputSchema, null, 2)}`).join('\n')}

When the user makes a request, determine which tool to use and extract the parameters. Respond with JSON in this format:
{
  "tool": "tool_name",
  "arguments": { ... },
  "explanation": "Brief explanation of what you're doing"
}

If the request is unclear or missing information, ask for clarification instead of making assumptions.

Important guidelines:
- Always respond with valid JSON
- Use the exact tool names from the list above
- Extract all required parameters from the user's request
- If a required parameter is missing, ask for it
- For role references, you can use either role names (like "admin", "manager") or role IDs
- For dates, use YYYY-MM-DD format
- Be helpful and conversational in your explanations`;

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
          // If no JSON found, return as explanation
          return { explanation: aiResponse };
        }
      } catch (parseError) {
        return { error: "Could not parse AI response", response: aiResponse };
      }
    } catch (error) {
      return { error: `Ollama API error: ${error.message}` };
    }
  }

  async executeMCPTool(toolName, args) {
    try {
      const result = await this.client.callTool({
        name: toolName,
        arguments: args
      });
      return result.content[0].text;
    } catch (error) {
      return `❌ Error executing ${toolName}: ${error.message}`;
    }
  }

  async startInteractiveSession() {
    console.log('🚀 Starting Ollama MCP Bridge...\n');

    // Check Ollama connection
    if (!await this.checkOllamaConnection()) {
      console.log('Failed to connect to Ollama. Please make sure Ollama is running.');
      console.log('Start Ollama with: ollama serve');
      return;
    }

    // Connect to MCP server
    if (!await this.connectToMCP()) {
      console.log('Failed to connect to MCP server. Exiting.');
      return;
    }

    const rl = readline.createInterface({
      input: process.stdin,
      output: process.stdout,
      prompt: '🦙 Ollama+MCP > '
    });

    console.log('\n🎉 Ollama + MCP Bridge Ready!');
    console.log(`💡 Powered by ${this.model} running locally`);
    console.log('\n📝 Try commands like:');
    console.log('  • "Create a new user named Sarah with email sarah@company.com and admin role"');
    console.log('  • "Show me all users in the system"');
    console.log('  • "Make a manager role with read and write permissions"');
    console.log('  • "Update user with ID 12345 to change their email"');
    console.log('  • "Delete the user with email john@example.com"');
    console.log('  • "Seed the database with default data"');
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

      // Process with Ollama
      const aiResponse = await this.processWithOllama(trimmedInput);

      if (aiResponse.error) {
        console.log('❌ Error:', aiResponse.error);
        if (aiResponse.response) {
          console.log('📝 Raw response:', aiResponse.response);
        }
      } else if (aiResponse.tool) {
        console.log(`🧠 AI Understanding: ${aiResponse.explanation}`);
        console.log(`🔧 Using tool: ${aiResponse.tool}`);
        console.log(`📋 Arguments:`, JSON.stringify(aiResponse.arguments, null, 2));

        // Execute MCP tool
        const result = await this.executeMCPTool(aiResponse.tool, aiResponse.arguments);
        console.log('\n📊 Result:');
        console.log(result);
      } else if (aiResponse.explanation) {
        console.log('💬 AI Response:', aiResponse.explanation);
      } else {
        console.log('💬 AI Response:', JSON.stringify(aiResponse, null, 2));
      }

      console.log('\n' + '─'.repeat(50));
      rl.prompt();
    });

    rl.on('close', () => {
      console.log('\n👋 Goodbye!');
      process.exit(0);
    });
  }

  // Method to change the model
  async changeModel(newModel) {
    try {
      const response = await axios.get(`${this.ollamaUrl}/api/tags`);
      const models = response.data.models || [];
      const modelExists = models.some(m => m.name.includes(newModel));
      
      if (modelExists) {
        this.model = newModel;
        console.log(`✅ Model changed to: ${this.model}`);
        return true;
      } else {
        console.log(`❌ Model '${newModel}' not found. Available models:`, models.map(m => m.name).join(', '));
        return false;
      }
    } catch (error) {
      console.log('❌ Error checking models:', error.message);
      return false;
    }
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
    case '--help':
      console.log(`
Ollama MCP Bridge - Connect Ollama with MongoDB CRUD API

Usage: node ollama-mcp-bridge.js [options]

Options:
  --model <name>        Ollama model to use (default: llama3.2)
  --ollama-url <url>    Ollama server URL (default: http://localhost:11434)
  --help               Show this help message

Examples:
  node ollama-mcp-bridge.js
  node ollama-mcp-bridge.js --model llama3.1
  node ollama-mcp-bridge.js --model codellama --ollama-url http://localhost:11434
      `);
      process.exit(0);
  }
}

// Start the bridge
const bridge = new OllamaMCPBridge(options);
bridge.startInteractiveSession().catch(console.error);