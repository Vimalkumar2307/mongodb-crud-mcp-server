// Quick test for specific prompts
const axios = require('axios');

async function testPrompts() {
  console.log('🧪 Testing Direct API Calls...\n');
  
  try {
    // Test 1: Show current users
    console.log('1. Current users:');
    const users = await axios.get('http://localhost:3000/api/users');
    console.log(`   Found ${users.data.length} users`);
    users.data.forEach(user => {
      console.log(`   - ${user.firstName} ${user.lastName} (${user.email})`);
    });
    
    // Test 2: Show current roles
    console.log('\n2. Current roles:');
    const roles = await axios.get('http://localhost:3000/api/roles');
    console.log(`   Found ${roles.data.length} roles`);
    roles.data.forEach(role => {
      console.log(`   - ${role.name}: ${role.permissions.join(', ')}`);
    });
    
    // Test 3: Create a new user
    console.log('\n3. Creating new user "Test User"...');
    const adminRole = roles.data.find(r => r.name === 'admin');
    if (adminRole) {
      const newUser = await axios.post('http://localhost:3000/api/users', {
        firstName: 'Test',
        lastName: 'User',
        email: 'test@example.com',
        password: 'testpass123',
        phone: '+1234567890',
        role: adminRole._id
      });
      console.log(`   ✅ Created user: ${newUser.data.firstName} ${newUser.data.lastName}`);
    }
    
    // Test 4: Create a new role
    console.log('\n4. Creating new role "editor"...');
    const newRole = await axios.post('http://localhost:3000/api/roles', {
      name: 'editor',
      description: 'Content editor with read and write permissions',
      permissions: ['read', 'write']
    });
    console.log(`   ✅ Created role: ${newRole.data.name}`);
    
  } catch (error) {
    if (error.response) {
      console.log(`   ❌ Error: ${error.response.data.error}`);
    } else {
      console.log(`   ❌ Error: ${error.message}`);
    }
  }
}

testPrompts();