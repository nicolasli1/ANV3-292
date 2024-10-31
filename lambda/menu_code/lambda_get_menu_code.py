import json

def lambda_handler(event, context):
    # TODO implement
    return {
        'statusCode': 200,
        'headers': {
            'Access-Control-Allow-Headers': 'Content-Type',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'OPTIONS,POST,GET'
        },       
        'body': json.dumps('El Menu del dia es Ajiaco')
    }
