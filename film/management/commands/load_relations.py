import json
from django.core.management.base import BaseCommand
from django.db import transaction
from film.models import Movie
from people.models import Cast, CrewMember, MovieCrew
from logs.logging_state import disable_logging


class Command(BaseCommand):
    """
    load relations from JSON file and set all crews and casts to movie.
    The Fifth command that is executed when starting the backend.
    """
    help = 'ایجاد روابط بین فیلم‌ها، بازیگران و عوامل تولید از فایل movie_relations.json'

    @transaction.atomic
    def handle(self, *args, **options):
        with disable_logging():
            file_path = "people/management/fixtures/movie_relations.json"

            try:
                with open(file_path, 'r', encoding='utf-8') as file:
                    relations_data = json.load(file)
            except FileNotFoundError:
                self.stdout.write(self.style.ERROR(f' file not found: {file_path}'))
                return
            failed_count = 0
            success_count = 0

            for item in relations_data:
                try:
                    movie_slug = item.get("movie_slug")

                    try:
                        movie = Movie.objects.get(slug=movie_slug)
                    except Movie.DoesNotExist:
                        self.stdout.write(self.style.WARNING(f'movie with slug: {movie_slug} not found.'))
                        continue

                    cast_slugs = item.get("casts", [])
                    if cast_slugs:
                        casts_queryset = Cast.objects.filter(slug__in=cast_slugs)
                        movie.casts.set(casts_queryset)

                    crew_list = item.get("crew", [])
                    for crew_data in crew_list:
                        crew_slug = crew_data.get("slug")
                        role = crew_data.get("role")

                        try:
                            crew_member = CrewMember.objects.get(slug=crew_slug)
                            MovieCrew.objects.update_or_create(
                                movie=movie,
                                crew=crew_member,
                                role=role
                            )
                        except CrewMember.DoesNotExist:
                            continue

                    success_count += 1
                except:
                    failed_count += 1

            self.stdout.write(
                self.style.SUCCESS(
                    f"Movies Reletions || success: {success_count} | failed: {failed_count}"
                )
            )
