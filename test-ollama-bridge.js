#!/usr/bin/env node

/**
 * Test script for Ollama MCP Bridge
 * This script tests the connection to both Ollama and the MCP server
 */

const axios = require('axios');
const { spawn } = require('child_process');

class OllamaBridgeTester {
  constructor() {
    this.ollamaUrl = 'http://localhost:11434';
    this.apiUrl = 'http://localhost:3000';
  }

  async testOllamaConnection() {
    console.log('🦙 Testing Ollama connection...');
    try {
      const response = await axios.get(`${this.ollamaUrl}/api/tags`);
      const models = response.data.models || [];
      
      if (models.length === 0) {
        console.log('⚠️  Ollama is running but no models are installed');
        console.log('💡 Install a model with: ollama pull llama3.2');
        return false;
      }
      
      console.log('✅ Ollama is running');
      console.log('📦 Available models:', models.map(m => m.name).join(', '));
      return true;
    } catch (error) {
      console.log('❌ Ollama connection failed:', error.message);
      console.log('💡 Make sure Ollama is running: ollama serve');
      return false;
    }
  }

  async testMongoDBAPI() {
    console.log('🍃 Testing MongoDB API connection...');
    try {
      const response = await axios.get(`${this.apiUrl}/`);
      console.log('✅ MongoDB API is running');
      console.log('📊 API Status:', response.data.status);
      return true;
    } catch (error) {
      console.log('❌ MongoDB API connection failed:', error.message);
      console.log('💡 Make sure your server is running: node server.js');
      return false;
    }
  }

  async testOllamaModel(modelName = 'llama3.2') {
    console.log(`🧠 Testing Ollama model: ${modelName}...`);
    try {
      const response = await axios.post(`${this.ollamaUrl}/api/generate`, {
        model: modelName,
        prompt: 'Hello! Please respond with just "Hello World" and nothing else.',
        stream: false,
        options: {
          temperature: 0.1
        }
      });

      const aiResponse = response.data.response;
      console.log('✅ Model is working');
      console.log('🤖 Test response:', aiResponse.substring(0, 100) + (aiResponse.length > 100 ? '...' : ''));
      return true;
    } catch (error) {
      console.log('❌ Model test failed:', error.message);
      if (error.response?.status === 404) {
        console.log(`💡 Model '${modelName}' not found. Install it with: ollama pull ${modelName}`);
      }
      return false;
    }
  }

  async testMCPServer() {
    console.log('🔌 Testing MCP server...');
    try {
      // Try to spawn the MCP server process
      const serverProcess = spawn('node', ['mcp-server.js'], {
        stdio: ['pipe', 'pipe', 'pipe'],
        cwd: process.cwd()
      });

      return new Promise((resolve) => {
        let output = '';
        let errorOutput = '';

        serverProcess.stdout.on('data', (data) => {
          output += data.toString();
        });

        serverProcess.stderr.on('data', (data) => {
          errorOutput += data.toString();
        });

        // Give it a few seconds to start
        setTimeout(() => {
          serverProcess.kill();
          
          if (errorOutput.includes('Error') || errorOutput.includes('error')) {
            console.log('❌ MCP server has errors:', errorOutput);
            resolve(false);
          } else {
            console.log('✅ MCP server can start');
            resolve(true);
          }
        }, 3000);
      });
    } catch (error) {
      console.log('❌ MCP server test failed:', error.message);
      return false;
    }
  }

  async runAllTests() {
    console.log('🧪 Running Ollama MCP Bridge Tests...\n');

    const results = {
      ollama: await this.testOllamaConnection(),
      mongodb: await this.testMongoDBAPI(),
      model: false,
      mcp: await this.testMCPServer()
    };

    if (results.ollama) {
      results.model = await this.testOllamaModel();
    }

    console.log('\n📋 Test Results Summary:');
    console.log('========================');
    console.log(`Ollama Connection: ${results.ollama ? '✅ PASS' : '❌ FAIL'}`);
    console.log(`MongoDB API: ${results.mongodb ? '✅ PASS' : '❌ FAIL'}`);
    console.log(`Ollama Model: ${results.model ? '✅ PASS' : '❌ FAIL'}`);
    console.log(`MCP Server: ${results.mcp ? '✅ PASS' : '❌ FAIL'}`);

    const allPassed = Object.values(results).every(result => result);
    
    console.log('\n🎯 Overall Status:');
    if (allPassed) {
      console.log('✅ All tests passed! You can run the bridge with:');
      console.log('   node ollama-mcp-bridge.js');
    } else {
      console.log('❌ Some tests failed. Please fix the issues above before running the bridge.');
      console.log('\n💡 Quick fixes:');
      if (!results.ollama) console.log('   - Start Ollama: ollama serve');
      if (!results.model) console.log('   - Install model: ollama pull llama3.2');
      if (!results.mongodb) console.log('   - Start API server: node server.js');
      if (!results.mcp) console.log('   - Check mcp-server.js file exists and has no syntax errors');
    }

    return allPassed;
  }
}

// Run tests if this script is executed directly
if (require.main === module) {
  const tester = new OllamaBridgeTester();
  tester.runAllTests().catch(console.error);
}

module.exports = OllamaBridgeTester;