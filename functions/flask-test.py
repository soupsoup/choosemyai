import os
import sys
import json

# Add the project root to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.join(current_dir, '..')
sys.path.insert(0, project_root)

def handler(event, context):
    try:
        print(f"Flask test function called with event: {event}")
        print(f"Context: {context}")
        
        # Try to import Flask app
        try:
            from main import app
            import serverless_wsgi
            print("Successfully imported Flask app and serverless_wsgi")
        except ImportError as import_error:
            print(f"Import error: {import_error}")
            return {
                'statusCode': 500,
                'body': json.dumps({
                    'error': 'Failed to import Flask app',
                    'message': str(import_error),
                    'sys.path': sys.path,
                    'current_dir': current_dir,
                    'project_root': project_root
                }),
                'headers': {
                    'Content-Type': 'application/json'
                }
            }
        
        # Handle the request
        try:
            return serverless_wsgi.handle_request(app, event, context)
        except Exception as wsgi_error:
            print(f"WSGI error: {wsgi_error}")
            return {
                'statusCode': 500,
                'body': json.dumps({
                    'error': 'WSGI handling error',
                    'message': str(wsgi_error)
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
                'message': str(e),
                'sys.path': sys.path
            }),
            'headers': {
                'Content-Type': 'application/json'
            }
        } 