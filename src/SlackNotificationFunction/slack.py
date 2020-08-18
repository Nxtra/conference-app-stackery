"""Functions for interacting with slack."""
import json
import requests

JSON_HEADER = {'Content-Type': 'application/json'}

def post_message(url, message):
    """Post a message to slack using a webhook url."""
    data = {'text': message}
    response = requests.post(url, data=json.dumps(data), headers=JSON_HEADER)
    return True if str(response.status_code).startswith("2") else False