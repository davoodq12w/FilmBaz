import json
from django.core.management.base import BaseCommand
from film.models import Genre


class Command(BaseCommand):
    help = "Load genres from json file"

    def handle(self, *args, **options):
        file_path = "film/management/fixtures/genres.json"

        try:
            with open(file_path, "r", encoding="utf-8") as file:
                genres = json.load(file)

            created_count = 0
            updated_count = 0

            for genre in genres:
                obj, created = Genre.objects.update_or_create(
                    slug=genre["slug"],
                    defaults={
                        "fa_name": genre["fa_name"],
                        "en_name": genre["en_name"],
                    }
                )

                if created:
                    created_count += 1
                else:
                    updated_count += 1

            self.stdout.write(
                self.style.SUCCESS(
                    f"Done! Created: {created_count}, Updated: {updated_count}"
                )
            )

        except FileNotFoundError:
            self.stdout.write(
                self.style.ERROR(f"File not found: {file_path}")
            )

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(str(e))
            )