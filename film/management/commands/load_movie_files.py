from django.core.management.base import BaseCommand
from film.models import Movie, MovieFile, MovieTrailer
from logs.logging_state import disable_logging


class Command(BaseCommand):
    help = "Load movie files"

    def handle(self, *args, **options):
        with disable_logging():
            movie_file_path = "movies/movies/sample_movie.mp4"
            trailer_path = "movies/trailers/sample_trailer.mp4"

            for movie in Movie.objects.all():
                MovieFile.objects.create(
                    file=movie_file_path,
                    movie=movie,
                )
                MovieTrailer.objects.create(
                    file=trailer_path,
                    movie=movie,
                )
