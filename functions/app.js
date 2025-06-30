exports.handler = async function(event, context) {
  const path = event.path;
  
  // Basic routing for the ChooseMyAI app
  if (path === '/' || path === '/index') {
    return {
      statusCode: 200,
      body: `
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>ChooseMyAI</title>
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
                    border-radius: 10px;
                    margin-bottom: 20px;
                    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                }
                .content {
                    background: white;
                    padding: 20px;
                    border-radius: 10px;
                    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                }
                h1 {
                    color: #333;
                    margin: 0;
                }
                .success {
                    color: #28a745;
                    font-weight: bold;
                }
                .info {
                    background: #e7f3ff;
                    padding: 15px;
                    border-radius: 5px;
                    margin: 20px 0;
                }
            </style>
        </head>
        <body>
            <div class="header">
                <h1>🎯 ChooseMyAI</h1>
                <p>Your AI tool directory is now live on Netlify!</p>
            </div>
            
            <div class="content">
                <h2 class="success">✅ Deployment Successful!</h2>
                
                <div class="info">
                    <h3>Current Status:</h3>
                    <ul>
                        <li>✅ Netlify functions are working</li>
                        <li>✅ JavaScript functions are deployed</li>
                        <li>⚠️ Python functions are not being deployed</li>
                        <li>⚠️ Flask app needs alternative approach</li>
                    </ul>
                </div>
                
                <h3>Next Steps:</h3>
                <p>Since Python functions aren't working on Netlify, we have a few options:</p>
                <ol>
                    <li><strong>Convert to JavaScript:</strong> Rewrite the Flask app using Node.js/Express</li>
                    <li><strong>Use a different platform:</strong> Deploy on Heroku, Railway, or similar</li>
                    <li><strong>Static site:</strong> Convert to a static site with JavaScript API calls</li>
                </ol>
                
                <h3>Function Test Results:</h3>
                <p><strong>JavaScript Functions:</strong> ✅ Working</p>
                <p><strong>Python Functions:</strong> ❌ Not deployed</p>
                <p><strong>Flask App:</strong> ❌ Not available</p>
            </div>
        </body>
        </html>
      `,
      headers: {
        'Content-Type': 'text/html'
      }
    };
  }
  
  // API endpoint
  if (path === '/api/status') {
    return {
      statusCode: 200,
      body: JSON.stringify({
        status: 'running',
        platform: 'netlify',
        functions: {
          javascript: 'working',
          python: 'not_deployed'
        },
        message: 'ChooseMyAI is running on Netlify with JavaScript functions'
      }),
      headers: {
        'Content-Type': 'application/json'
      }
    };
  }
  
  // 404 for other routes
  return {
    statusCode: 404,
    body: JSON.stringify({
      error: 'Page not found',
      path: path,
      message: 'This route is not implemented in the JavaScript version'
    }),
    headers: {
      'Content-Type': 'application/json'
    }
  };
};
 