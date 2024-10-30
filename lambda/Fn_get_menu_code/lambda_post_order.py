import json
import boto3
from botocore.exceptions import ClientError

# Specify the DynamoDB table name
TABLE_NAME = 'My_primera_global_table_292'

def lambda_handler(event, context):
    dynamodb = boto3.resource('dynamodb')
    # Reference the DynamoDB table
    table = dynamodb.Table(TABLE_NAME)
    
    # Parse the body of the request (assuming it's a JSON body)
    try:
        body = json.loads(event['body'])
    except KeyError:
        return {
            'statusCode': 400,
            'body': json.dumps('Error: Request body is required.')
        }
    
    name = body.get('name')
    cantidad = body.get('cantidad')
    identity = body.get('pk')
    
    # Validate required fields
    if not name or not cantidad:
        return {
            'statusCode': 400,
            'body': json.dumps(f'Error: name and cantidad are required.')
        }
    
    # Save the data
    try:
        table.put_item(
            Item={
                'id_pk': identity,
                'name': name,
                'cantidad': cantidad
            }
        )
        
        # Prepare the successful response
        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'POST'
            },
            'body': json.dumps({"message": "Record created successfully"})
        }
    except ClientError as e:
        # Handle DynamoDB errors
        return {
            'statusCode': 500,
            'body': json.dumps(f'Error inserting item into DynamoDB: {str(e)}')
        }