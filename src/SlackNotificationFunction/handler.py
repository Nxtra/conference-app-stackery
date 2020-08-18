import json
import os
import slack
import config
from aws_lambda_powertools import Logger, Tracer, Metrics
from aws_lambda_powertools.metrics import MetricUnit

logger = Logger()
tracer = Tracer()
metrics = Metrics()

SLACK_WEBHOOK_URL = os.environ['SLACK_WEBHOOK_URL']

@metrics.log_metrics
@tracer.capture_lambda_handler
@logger.inject_lambda_context
def handle(event, context):
    # Log the event argument for debugging and for use in local development.
    logger.info(json.dumps(event))

    for record in event['Records']:
        if record['eventName'] != 'INSERT':
            continue
        new_image = record.get('dynamodb').get('NewImage')
        creator = new_image.get('creator')["S"]
        learning = new_image.get('learning')["S"]
        logger.info(f'learning: {learning}, creator {creator}')
        logger.structure_logs(append=True, learning_id=new_image.get('id')['S'])
        message = compose_message(creator, learning)
        send_slack_message(message)
    logger.info('Successfully processed %s records.' % str(len(event['Records'])))


def compose_message(creator, learning):
    return f"{creator} add a new learning: {learning}"

@tracer.capture_method
def send_slack_message(message):
    success = slack.post_message(config.SLACK_WEBHOOK_URL, message)
    if success:
        metrics.add_dimension(name="environment", value="dev")
        metrics.add_metric(name="SlackNotificationSend", unit=MetricUnit.Count, value=1)