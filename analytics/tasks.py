import hashlib
import hmac
import time
import requests
from celery import shared_task
from decouple import config

BUILD_MODEL_PASSWORD = config("BUILD_MODEL_PASSWORD")
BUILD_MODEL_URL = "http://ml_service:8002/build_model/"


@shared_task()
def build_model():
    timestamp = str(int(time.time()))

    message = f"POST\n/build_model\n{timestamp}"

    signature = hmac.new(
        BUILD_MODEL_PASSWORD.encode(),
        message.encode(),
        hashlib.sha256,
    ).hexdigest()

    headers = {
        "X-Timestamp": timestamp,
        "X-Signature": signature,
    }

    response = requests.post(
        BUILD_MODEL_URL,
        headers=headers,
        timeout=(30, 3600),
    )

    response.raise_for_status()
    print(response.text)
