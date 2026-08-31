from pathlib import Path
from django.core.management.base import BaseCommand
from analytics.utils import DatasetBuilder
from datetime import datetime


class Command(BaseCommand):
    help = "Build training dataset for recommendation system."

    def handle(self, *args, **options):
        builder = DatasetBuilder()
        df = builder.build()

        output_dir = Path("ml_service/datasets/raw")
        output_dir.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = output_dir / f"dataset_{timestamp}.csv"

        df.to_csv(output_file, index=False)
