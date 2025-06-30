const express = require('express');
const serverless = require('serverless-http');

const app = express();

app.get('/', (req, res) => {
  res.json({ 
    message: 'Test function working!', 
    timestamp: new Date().toISOString(),
    noEjs: true
  });
});

module.exports.handler = serverless(app); 