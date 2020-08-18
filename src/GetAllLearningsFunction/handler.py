import json
def handle(event, context):
    # Log the event argument for debugging and for use in local development.
    print(json.dumps(event))

    return {}