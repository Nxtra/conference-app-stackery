import json
import os
import time
import uuid

import boto3

dynamodb = boto3.client('dynamodb')
learnings_table_name = os.environ['TABLE_NAME']


def handle(event, context):
    # Log the event argument for debugging and for use in local development.
    learning = create_learning(json.loads(event['body']))
    print(f'learning that was created: {json.dumps(learning)}')

    return {
        'learning': learning
    }


def create_learning(learning_info):
    print(json.dumps(learning_info))
    current_time_in_millis = int(round(time.time() * 1000))
    learning = {
        'creator': learning_info.get('creator'),
        'category': learning_info.get('category'),
        'session': learning_info.get('session'),
        'learning': learning_info.get('learning'),
        'creationTimeStamp': str(current_time_in_millis)
    }
    print(f'will create learning ${learning}')
    save_learning(learning)
    return learning


def save_learning(learning):
    learning_id = str(uuid.uuid4())
    print(learning)
    item = {
        'id': {'S': learning_id},
        'creator': {'S': learning['creator']},
        'category': {'S': learning['category']},
        'session': {'S': learning['session']},
        'learning': {'S': str(learning['learning'])},
        'creationTimeStamp': {'S': learning['creationTimeStamp']}
    }
    print(item)
    response = dynamodb.put_item(
        TableName=learnings_table_name,
        Item=item
    )
    print("UPLOADED ITEM")
