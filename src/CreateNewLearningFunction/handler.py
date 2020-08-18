import json
import os
import time
import uuid

import boto3

from aws_lambda_powertools import Logger, Tracer, Metrics
from aws_lambda_powertools.metrics import MetricUnit


logger = Logger()
tracer = Tracer()
metrics = Metrics()
cold_start = True


dynamodb = boto3.client('dynamodb')
learnings_table_name = os.environ['TABLE_NAME']


@metrics.log_metrics(capture_cold_start_metric=True)
@logger.inject_lambda_context
@tracer.capture_lambda_handler
def handle(event, context):
    logger.info("Received new event")

    incoming = json.loads(event['body'])
    if not is_valid_learning(incoming):
        return {
            'statusCode': 400
        }

    new_learning = add_non_required_keys(incoming)

    new_learning = create_learning(new_learning)
    logger.info(f'Learning successfully created')

    metrics.add_dimension(name="environment", value="dev")
    metrics.add_metric(name="LearningCreatedSuccess", unit=MetricUnit.Count, value=1)

    return {
        'learning': new_learning
    }


@tracer.capture_method
def is_valid_learning(learning_info):
    for k in ['creator', 'learning']:
        if not k in learning_info or len(learning_info[k]) == 0:
            logger.warning(f'Incoming object has incorrect key {k}: missing or empty')
            metrics.add_metric(name="InvalidIncomingRequest", unit=MetricUnit.Count, value=1)
            return False
    logger.info('Validated')
    return True


def add_non_required_keys(learning):
    for k,v in {'session': 'unknown', 'category': 'general'}.items():
        if not k in learning or len(learning[k]) == 0:
            learning[k] = v
    return learning


def create_learning(learning_info):
    logger.structure_logs(append=True, session=learning_info["session"])
    current_time_in_millis = int(round(time.time() * 1000))
    learning = {
        'creator': learning_info.get('creator'),
        'category': learning_info.get('category'),
        'session': learning_info.get('session'),
        'learning': learning_info.get('learning'),
        'creationTimeStamp': str(current_time_in_millis)
    }
    save_learning(learning)
    return learning


def save_learning(learning):
    logger.debug(f'Saving learning: ${learning}')
    learning_id = str(uuid.uuid4())
    logger.info(learning)
    logger.structure_logs(append=True, learning_id=learning_id)
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




"""
# This is no longer necessary since we have the option to add this metric
def is_cold_start():
    global cold_start
    if cold_start:
        logger.info('This is a cold start')
        cold_start = False
        return True
    return False


def configure_cold_start_metric():
    logger.info('Counting up cold start')
    metrics.add_metric(name="ColdStart", unit=MetricUnit.Count, value=1)
"""