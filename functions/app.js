exports.handler = async (event, context) => {
  const path = event.path || '/';
  const method = event.httpMethod || 'GET';

  console.log(`Request: ${method} ${path}`);

  // Simple HTML content
  const htmlContent = `
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ChooseMyAI - AI Tool Directory</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }
        .header {
            background: white;
            padding: 20px;
            border-radius: 8px;
            margin-bottom: 20px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .tools-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
            gap: 20px;
            margin-top: 20px;
        }
        .tool-card {
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .tool-card h3 {
            margin-top: 0;
            color: #333;
        }
        .tool-card p {
            color: #666;
            line-height: 1.5;
        }
        .nav {
            display: flex;
            gap: 20px;
            margin-bottom: 20px;
        }
        .nav a {
            color: #007bff;
            text-decoration: none;
        }
        .nav a:hover {
            text-decoration: underline;
        }
        .debug {
            background: #e9ecef;
            padding: 10px;
            border-radius: 4px;
            margin-top: 20px;
            font-family: monospace;
            font-size: 12px;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>ChooseMyAI</h1>
        <p>Discover the best AI tools for your needs</p>
        <div class="nav">
            <a href="/">Home</a>
            <a href="/api/tools">API</a>
            <a href="/.netlify/functions/hello">Test Function</a>
        </div>
    </div>

    <div id="content">
        <h2>Featured AI Tools</h2>
        <div class="tools-grid">
            <div class="tool-card">
                <h3>ChatGPT</h3>
                <p>Advanced language model for conversation and text generation</p>
                <p><strong>Website:</strong> <a href="https://chat.openai.com" target="_blank">https://chat.openai.com</a></p>
                <p><strong>Pricing:</strong> Free tier available</p>
            </div>
            <div class="tool-card">
                <h3>Midjourney</h3>
                <p>AI art generation tool for creating stunning images</p>
                <p><strong>Website:</strong> <a href="https://midjourney.com" target="_blank">https://midjourney.com</a></p>
                <p><strong>Pricing:</strong> Paid subscription</p>
            </div>
            <div class="tool-card">
                <h3>GitHub Copilot</h3>
                <p>AI-powered code completion and generation tool</p>
                <p><strong>Website:</strong> <a href="https://github.com/features/copilot" target="_blank">GitHub Copilot</a></p>
                <p><strong>Pricing:</strong> Subscription required</p>
            </div>
        </div>
    </div>

    <div class="debug">
        <strong>Debug Info:</strong><br>
        Path: ${path}<br>
        Method: ${method}<br>
        Timestamp: ${new Date().toISOString()}<br>
        Function: Working ✅
    </div>
</body>
</html>`;

  // Handle API routes
  if (path.startsWith('/api/')) {
    if (path === '/api/tools') {
      return {
        statusCode: 200,
        headers: {
          'Content-Type': 'application/json',
          'Access-Control-Allow-Origin': '*'
        },
        body: JSON.stringify({
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
            },
            {
              id: 3,
              name: 'GitHub Copilot',
              description: 'AI-powered code completion and generation tool',
              website: 'https://github.com/features/copilot',
              pricing: 'Subscription required'
            }
          ],
          timestamp: new Date().toISOString(),
          path: path,
          method: method
        }),
      };
    }
    
    // API 404
    return {
      statusCode: 404,
      headers: {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*'
      },
      body: JSON.stringify({
        error: 'API endpoint not found',
        path: path,
        availableEndpoints: ['/api/tools']
      }),
    };
  }

  // Serve HTML for all other routes
  return {
    statusCode: 200,
    headers: {
      'Content-Type': 'text/html',
      'Cache-Control': 'no-cache'
    },
    body: htmlContent,
  };
}; 