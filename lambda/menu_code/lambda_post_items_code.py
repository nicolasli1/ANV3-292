import json
import boto3

def lambda_handler(event, context):
    # Inicializa el cliente de DynamoDB
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('My_primera_global_table_292')
    
    try:
        # Verifica si el método es POST
        if event['httpMethod'] == 'POST':
            body = json.loads(event['body'])
            # Inserta el ítem en la tabla DynamoDB
            response = table.put_item(Item=body)
            return {
                'statusCode': 200,
                'headers': {
                    'Access-Control-Allow-Headers': 'Content-Type',
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Methods': 'OPTIONS,POST,GET'
                },
                'body': json.dumps({'message': 'Item inserted successfully', 'response': response})
            }
        
        # Si no es POST, devuelve un error
        return {
            'statusCode': 400,
            'headers': {
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'OPTIONS,POST,GET'
            },
            'body': json.dumps({'error': 'Unsupported HTTP method, use POST'})
        }
        
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': {
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'OPTIONS,POST,GET'
            },
            'body': json.dumps({'error': str(e)})
        }