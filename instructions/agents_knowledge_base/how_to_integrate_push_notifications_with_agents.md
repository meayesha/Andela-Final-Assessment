# How to Integrate Push Notifications with Agents

You can send push notifications (e.g., via Pushover) from agent tool calls to log user actions or important events.

## Example: Sending a Push Notification

```python
import requests
import os

def push(text):
    requests.post(
        "https://api.pushover.net/1/messages.json",
        data={
            "token": os.getenv("PUSHOVER_TOKEN"),
            "user": os.getenv("PUSHOVER_USER"),
            "message": text,
        }
    )
```

Use this function in your tool logic to notify you of key events, such as a user providing their email or asking an unknown question.
