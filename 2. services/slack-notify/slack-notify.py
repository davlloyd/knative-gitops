import json, os
import requests

from flask import Flask, request

app = Flask(__name__)

@app.route('/', methods=['POST'])
def send():
    app.logger.info("Posting Slack message")

    webhook_url = os.getenv("SLACK_URL")
    app.logger.info(webhook_url)

    data = request.get_json()
    message = data.get("message")
    app.logger.info("message content")
    app.logger.info(message)

    slack_data = {'text': message}

    response = requests.post(
        webhook_url, data=json.dumps(slack_data),
        headers={'Content-Type': 'application/json'}
    )

    app.logger.info(response.status_code)

    return {"status": response.status_code}

if __name__ == "__main__":
    app.run(debug=True,host='0.0.0.0',port=int(os.environ.get('PORT', 8080)))

