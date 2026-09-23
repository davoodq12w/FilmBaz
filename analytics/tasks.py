import hashlib
import hmac
import time
import requests
from celery import shared_task
from decouple import config
from pathlib import Path
from analytics.utils import DatasetBuilder
from datetime import datetime
from ml_service.datasets.generator import generate_dataset

BUILD_MODEL_PASSWORD = config("BUILD_MODEL_PASSWORD")
BUILD_MODEL_URL = "http://ml_service:8002/build_model/"


@shared_task()
def build_model():
    timestamp = str(int(time.time()))

    message = f"POST\n/build_model/\n{timestamp}"

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


@shared_task()
def build_row_dataset():
    builder = DatasetBuilder()
    df = builder.build()

    if len(df) < 1000:
        df = generate_dataset(10000)  # generate random data set.

    output_dir = Path("ml_service/datasets/raw")
    output_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = output_dir / f"dataset_{timestamp}.csv"

    df.to_csv(output_file, index=False)
