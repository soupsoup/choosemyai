import os
import sys
import json

def handler(event, context):
    try:
        print(f"Function called with event: {event}")
        print(f"Context: {context}")
        
        # Get the path from the event
        path = event.get('path', '/')
        
        # If it's the root path, return a simple HTML response
        if path == '/' or path == '/.netlify/functions/app':
            return {
                'statusCode': 200,
                'body': '''
                <!DOCTYPE html>
                <html>
                <head>
                    <title>ChooseMyAI - Function Working!</title>
                    <style>
                        body { font-family: Arial, sans-serif; text-align: center; padding: 50px; }
                        .success { color: green; font-size: 24px; }
                    </style>
                </head>
                <body>
                    <h1 class="success">✅ ChooseMyAI Function is Working!</h1>
                    <p>The serverless function is successfully deployed and responding.</p>
                    <p>Path: ''' + path + '''</p>
                </body>
                </html>
                ''',
                'headers': {
                    'Content-Type': 'text/html'
                }
            }
        
        # For other paths, return JSON
        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'Function is working!',
                'path': path,
                'method': event.get('httpMethod', 'unknown')
            }),
            'headers': {
                'Content-Type': 'application/json'
            }
        }
        
    except Exception as e:
        print(f"Error in function: {e}")
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': 'Function error',
                'message': str(e)
            }),
            'headers': {
                'Content-Type': 'application/json'
            }
        }