// Simple connectivity test
const axios = require('axios');

async function quickTest() {
  try {
    console.log('Testing API...');
    const response = await axios.get('http://localhost:3000/api/roles');
    console.log('✅ API working! Found', response.data.length, 'roles');
    
    if (response.data.length === 0) {
      console.log('Seeding database...');
      await axios.post('http://localhost:3000/api/seed');
      console.log('✅ Database seeded');
    }
    
    const users = await axios.get('http://localhost:3000/api/users');
    console.log('✅ Found', users.data.length, 'users');
    
  } catch (error) {
    console.error('❌ Error:', error.message);
  }
}

quickTest();