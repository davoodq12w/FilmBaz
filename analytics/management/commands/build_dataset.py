from pathlib import Path
from django.core.management.base import BaseCommand
from analytics.utils import DatasetBuilder


class Command(BaseCommand):
    help = "Build training dataset for recommendation system."

    def handle(self, *args, **options):
        self.stdout.write("Building dataset...")

        builder = DatasetBuilder()
        df = builder.build()

        output_dir = Path("analytics/traning_datas")
        output_dir.mkdir(parents=True, exist_ok=True)

        output_file = output_dir / "train_dataset.csv"

        df.to_csv(output_file, index=False)

        self.stdout.write(
            self.style.SUCCESS(
                f"Dataset created successfully.\n"
                f"Rows: {len(df)}\n"
                f"Columns: {len(df.columns)}\n"
                f"Saved to: {output_file}"
            )
        )
