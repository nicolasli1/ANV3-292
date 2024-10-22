import json
import boto3

def lambda_handler(event, context):
    # Inicializa el cliente de DynamoDB
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('My_primera_global_table_292')

    name = event['name']
    cantidad = event['cantidad']

    # Guarda los datos 
    table.put_item(
    item={
            'name': name,
            'cantidad': cantidad
         }
    )
   
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
            'body': json.dumps(items)
        }
        
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }
