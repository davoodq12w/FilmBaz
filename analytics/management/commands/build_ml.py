from pathlib import Path
from django.core.management.base import BaseCommand
from analytics.utils import DatasetBuilder
from datetime import datetime
from ml_service.datasets.generator import generate_dataset
from ml_service.app.preprocessing.pipeline import get_processed_dataset
from ml_service.app.training.trainer import train_model


class Command(BaseCommand):
    help = "Build training dataset for recommendation system."

    def handle(self, *args, **options):
        self.pipline()

    def build_dataset(self):
        builder = DatasetBuilder()
        df = builder.build()
        if df.count() >= 10000:

            output_dir = Path("ml_service/datasets/raw")
            output_dir.mkdir(parents=True, exist_ok=True)

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = output_dir / f"dataset_{timestamp}.csv"

            df.to_csv(output_file, index=False)
        else:
            generate_dataset(10000)

    def pipline(self):
        self.stdout.write(
            self.style.NOTICE("buidling dataset...")
        )
        self.build_dataset()

        self.stdout.write(
            self.style.NOTICE("preprocessing dataset...")
        )
        get_processed_dataset()

        self.stdout.write(
            self.style.NOTICE("buidling recommender model...")
        )
        train_model()
