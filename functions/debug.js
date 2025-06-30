const fs = require('fs');
const path = require('path');

exports.handler = async function(event, context) {
  try {
    // List all files in the functions directory
    const functionsDir = path.join(__dirname);
    const files = fs.readdirSync(functionsDir);
    
    // Check if Python files exist
    const pythonFiles = files.filter(file => file.endsWith('.py'));
    const jsFiles = files.filter(file => file.endsWith('.js'));
    
    return {
      statusCode: 200,
      body: JSON.stringify({
        message: "Debug information",
        functionFiles: files,
        pythonFiles: pythonFiles,
        jsFiles: jsFiles,
        currentDir: __dirname,
        event: event
      }),
      headers: {
        'Content-Type': 'application/json'
      }
    };
  } catch (error) {
    return {
      statusCode: 500,
      body: JSON.stringify({
        error: 'Debug function error',
        message: error.message
      }),
      headers: {
        'Content-Type': 'application/json'
      }
    };
  }
}; 