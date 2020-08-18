import json
import os
import time
import uuid

import boto3

from aws_lambda_powertools import Logger
# POWERTOOLS_SERVICE_NAME defined
logger = Logger()

dynamodb = boto3.client('dynamodb')
learnings_table_name = os.environ['TABLE_NAME']

@logger.inject_lambda_context
def handle(event, context):
    # Log the event argument for debugging and for use in local development.
    logger.info("received new event")


    learning = create_learning(json.loads(event['body']))
    logger.info(f'learning that was created: {json.dumps(learning)}')

    return {
        'learning': learning
    }


def validate_learning_info(learning_info):
    logger.info('validated')


def create_learning(learning_info):
    logger.info(json.dumps(learning_info))
    current_time_in_millis = int(round(time.time() * 1000))
    learning = {
        'creator': learning_info.get('creator'),
        'category': learning_info.get('category'),
        'session': learning_info.get('session'),
        'learning': learning_info.get('learning'),
        'creationTimeStamp': str(current_time_in_millis)
    }
    logger.info(f'will create learning ${learning}')
    save_learning(learning)
    return learning


def save_learning(learning):
    learning_id = str(uuid.uuid4())
    logger.info(learning)
    item = {
        'id': {'S': learning_id},
        'creator': {'S': learning['creator']},
        'category': {'S': learning['category']},
        'session': {'S': learning['session']},
        'learning': {'S': str(learning['learning'])},
        'creationTimeStamp': {'S': learning['creationTimeStamp']}
    }
    logger.info(item)
    response = dynamodb.put_item(
        TableName=learnings_table_name,
        Item=item
    )
    logger.info("UPLOADED ITEM")
