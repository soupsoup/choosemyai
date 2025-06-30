import json

def handler(event, context):
    return {
        'statusCode': 200,
        'body': json.dumps({
            'message': 'Test function is working!',
            'event': event
        }),
        'headers': {
            'Content-Type': 'application/json'
        }
    } 