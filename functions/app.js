const express = require('express');
const serverless = require('serverless-http');
const path = require('path');

const app = express();

// Middleware
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

// Serve static files
app.use('/static', express.static(path.join(__dirname, '../static')));

// Routes
app.get('/', (req, res) => {
  res.sendFile(path.join(__dirname, '../static/index.html'));
});

app.get('/api/home', (req, res) => {
  res.json({ 
    tools: [
      {
        id: 1,
        name: 'ChatGPT',
        description: 'Advanced language model for conversation and text generation',
        website: 'https://chat.openai.com',
        pricing: 'Free tier available'
      },
      {
        id: 2,
        name: 'Midjourney',
        description: 'AI art generation tool for creating stunning images',
        website: 'https://midjourney.com',
        pricing: 'Paid subscription'
      }
    ],
    categories: [
      { id: 1, name: 'AI Writing' },
      { id: 2, name: 'AI Image Generation' }
    ],
    user: null
  });
});

// Error handler
app.use((err, req, res, next) => {
  console.error(err.stack);
  res.status(500).json({ error: 'Something went wrong!' });
});

// 404 handler
app.use((req, res) => {
  res.status(404).json({ error: 'Page not found' });
});

module.exports.handler = serverless(app);
 