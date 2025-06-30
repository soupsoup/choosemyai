import json

def handler(event, context):
    return {
        'statusCode': 200,
        'body': json.dumps({
            'message': 'Python function is working!',
            'path': event.get('path', 'unknown'),
            'method': event.get('httpMethod', 'unknown')
        }),
        'headers': {
            'Content-Type': 'application/json'
        }
    } 