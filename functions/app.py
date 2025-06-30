import os
import sys
import json

def handler(event, context):
    try:
        print(f"Function called with event: {event}")
        print(f"Context: {context}")
        
        # For now, just return a simple response to test if the function works
        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'Function is working!',
                'path': event.get('path', 'unknown'),
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