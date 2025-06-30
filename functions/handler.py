import json

def handler(event, context):
    return {
        'statusCode': 200,
        'body': json.dumps({
            'message': 'Python handler function working!',
            'event': event
        }),
        'headers': {
            'Content-Type': 'application/json'
        }
    } 