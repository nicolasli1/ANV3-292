import json
import boto3
from decimal import Decimal

   # Function to convert Decimal to int/float for JSON serialization
def decimal_default(obj):
    if isinstance(obj, Decimal):
        # Convert Decimal to float or int based on your data requirements
        return int(obj) if obj % 1 == 0 else float(obj)
    raise TypeError
def lambda_handler(event, context):
    # Inicializa el cliente de DynamoDB
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('My_primera_global_table_292')
   
    # Recupera todos los elementos de la tabla
    try:
        response = table.scan()
        items = response['Items']

        # Manejo de paginación si hay más elementos
        while 'LastEvaluatedKey' in response:
            response = table.scan(ExclusiveStartKey=response['LastEvaluatedKey'])
            items.extend(response['Items'])

        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'GET'
            },
            'body': json.dumps(items, default=decimal_default)  # Use custom serialization
        }
        
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }
