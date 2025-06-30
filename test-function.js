const { handler } = require('./functions/app');

// Mock event and context
const event = {
  httpMethod: 'GET',
  path: '/',
  headers: {},
  queryStringParameters: null,
  body: null
};

const context = {};

// Test the function
async function testFunction() {
  try {
    const result = await handler(event, context);
    console.log('Function result:', result);
    console.log('Status code:', result.statusCode);
    console.log('Body preview:', result.body.substring(0, 200) + '...');
  } catch (error) {
    console.error('Function error:', error);
  }
}

testFunction(); 