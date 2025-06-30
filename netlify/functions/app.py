import os
import sys
import json

# Add the project root to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.join(current_dir, '..', '..')
sys.path.insert(0, project_root)

try:
    from main import app
    import serverless_wsgi
    
    def handler(event, context):
        print(f"Function called with event: {event}")
        print(f"Context: {context}")
        return serverless_wsgi.handle_request(app, event, context)
        
except ImportError as e:
    print(f"Import error: {e}")
    def handler(event, context):
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': 'Failed to import Flask app',
                'message': str(e),
                'sys.path': sys.path
            }),
            'headers': {
                'Content-Type': 'application/json'
            }
        }