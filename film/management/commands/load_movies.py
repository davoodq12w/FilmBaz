import json
from django.core.management.base import BaseCommand
from django.db import transaction
from film.models import Movie, Genre


class Command(BaseCommand):
    help = "Import movies from json file"

    @transaction.atomic
    def handle(self, *args, **options):

        file_path = "film/management/fixtures/movies.json"

        try:

            with open(file_path, "r", encoding="utf-8") as file:
                movies = json.load(file)

            created_count = 0
            updated_count = 0

            for data in movies:

                movie, created = Movie.objects.update_or_create(
                    slug=data["slug"],
                    defaults={
                        "fa_title": data["fa_title"],
                        "orj_title": data["orj_title"],
                        "rate": data["rate"],
                        "release_date": data["release_date"],
                        "country": data["country"],
                        "runtime": data["runtime"],
                        "is_serie": data["is_serie"],
                        "adult": data["adult"],
                    }
                )

                genres = Genre.objects.filter(
                    slug__in=data["genres"]
                )

                movie.genres.set(genres)

                if created:
                    created_count += 1
                else:
                    updated_count += 1

            self.stdout.write(
                self.style.SUCCESS(
                    f"فیلم ها || ساخته شده ها: {created_count} | آپدیت شده ها: {updated_count}"
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