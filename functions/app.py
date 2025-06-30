import os
import sys
import json

# Add the project root to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.join(current_dir, '..')
sys.path.insert(0, project_root)

def handler(event, context):
    try:
        print(f"Function called with event: {event}")
        print(f"Context: {context}")
        
        # Import Flask app
        from main import app
        import serverless_wsgi
        
        # Handle the request
        return serverless_wsgi.handle_request(app, event, context)
        
    except ImportError as e:
        print(f"Import error: {e}")
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
    except Exception as e:
        print(f"Unexpected error: {e}")
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': 'Unexpected error',
                'message': str(e)
            }),
            'headers': {
                'Content-Type': 'application/json'
            }
        }