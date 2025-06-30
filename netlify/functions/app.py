import os
import sys

# Add the project root to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from main import app
import serverless_wsgi

def handler(event, context):
    return serverless_wsgi.handle_request(app, event, context)