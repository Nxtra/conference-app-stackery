import json
import os

import boto3

learnings_table_name = os.environ['TABLE_NAME']
dynamodb = boto3.resource('dynamodb', region_name='eu-west-1')
table = dynamodb.Table(learnings_table_name)


def handle(event, context):
    # Log the event argument for debugging and for use in local development.
    print(json.dumps(event))
    data = scan()

    return {
        'learnings': data
    }


def scan():
    response = table.scan()
    data = response['Items']

    while 'LastEvaluatedKey' in response:
        response = table.scan(ExclusiveStartKey=response['LastEvaluatedKey'])
        data.extend(response['Items'])

    return data
