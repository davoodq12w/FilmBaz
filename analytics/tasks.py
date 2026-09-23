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
    """
    Celery Task used for request to ml service for building new recommender ml model.
    task runs with Celery Beat.
    """
    timestamp = str(int(time.time()))
    message = f"POST\n/build_model/\n{timestamp}"

    # this signature uses for more security by using time
    signature = hmac.new(
        BUILD_MODEL_PASSWORD.encode(),
        message.encode(),
        hashlib.sha256,
    ).hexdigest()

    headers = {
        "X-Timestamp": timestamp,
        "X-Signature": signature,
    }  # ml service most have the BUILD_MODEL_PASSWORD to check signature that is true or not.

    response = requests.post(
        BUILD_MODEL_URL,
        headers=headers,
        timeout=(30, 3600),
    )

    response.raise_for_status()  # if there was any error rised automaticly
    print(response.text)


@shared_task()
def build_row_dataset():
    """
    Celery Task used for creating new row dataset for recommender ml model.
    task runs with Celery Beat.
    """
    builder = DatasetBuilder()
    df = builder.build()

    if len(df) < 1000:  # if lenght of Real dataset is lesser than 1000.
        df = generate_dataset(10000)  # generate random data set.

    output_dir = Path("ml_service/datasets/raw")
    output_dir.mkdir(parents=True, exist_ok=True)

    # use datetime in the name of csv file for date ordering
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = output_dir / f"dataset_{timestamp}.csv"

    df.to_csv(output_file, index=False)
