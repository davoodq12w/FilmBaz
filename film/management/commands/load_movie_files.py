from django.core.management.base import BaseCommand
from film.models import Movie, MovieEpisode, MovieTrailer
from logs.logging_state import disable_logging


class Command(BaseCommand):
    help = "Load movie files"

    def handle(self, *args, **options):
        with disable_logging():
            try:
                movie_file_path = "movies/movies/sample_movie.mp4"
                trailer_path = "movies/trailers/sample_trailer.mp4"

                file_created_count = 0
                file_updated_count = 0
                trailer_created_count = 0
                trailer_updated_count = 0

                for movie in Movie.objects.all():
                    obj, file_created = MovieEpisode.objects.update_or_create(
                        file=movie_file_path,
                        movie=movie,
                        minute=5,
                    )
                    if file_created:
                        file_created_count += 1
                    else:
                        file_updated_count += 1

                    obj, trailer_created = MovieTrailer.objects.update_or_create(
                        file=trailer_path,
                        movie=movie,
                    )
                    if trailer_created:
                        trailer_created_count += 1
                    else:
                        trailer_updated_count += 1

                self.stdout.write(
                    self.style.SUCCESS(
                        f"فایل ها || ساخته شده ها: {file_created_count} | آپدیت شده ها: {file_updated_count}"
                    )
                )
                self.stdout.write(
                    self.style.SUCCESS(
                        f"فایل ها || ساخته شده ها: {trailer_created_count} | آپدیت شده ها: {trailer_updated_count}"
                    )
                )

            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f"Error: {e}")
                )
