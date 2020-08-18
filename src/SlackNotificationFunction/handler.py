import json
import os
import slack
import config

SLACK_WEBHOOK_URL = os.environ['SLACK_WEBHOOK_URL']

def handle(event, context):
    # Log the event argument for debugging and for use in local development.
    print(json.dumps(event))

    for record in event['Records']:
        if record['eventName'] != 'INSERT':
            continue
        new_image = record.get('dynamodb').get('NewImage')
        creator = new_image.get('creator')["S"]
        learning = new_image.get('learning')["S"]
        print(f'learning: {learning}, creator {creator}')
        message = compose_message(creator, learning)
        send_slack_message(message)
    print('Successfully processed %s records.' % str(len(event['Records'])))


def compose_message(creator, learning):
    return f"{creator} add a new learning: {learning}"


def send_slack_message(message):
    """Lambda function handler."""
    slack.post_message(config.SLACK_WEBHOOK_URL, message)