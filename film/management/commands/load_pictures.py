from django.core.management.base import BaseCommand

from film.models import Movie
from people.models import Cast, CrewMember


class Command(BaseCommand):
    help = "Set image paths for crews, casts, and movie posters/backdrops."

    def handle(self, *args, **options):
        self.set_crew_photos()
        self.set_cast_photos()
        self.set_movie_photos()

    def set_crew_photos(self):
        success_saves = 0
        failed_saves = 0

        for crew in CrewMember.objects.all():
            try:
                crew.image = f"people/crews/{crew.en_name.replace(' ', '_')}.webp"
                crew.save(update_fields=["image"])
                success_saves += 1
            except Exception as e:
                failed_saves += 1
                self.stdout.write(self.style.ERROR(f"{crew.en_name} failed"))
                self.stdout.write(self.style.ERROR(f"error: {e}"))

        self.stdout.write(
            self.style.SUCCESS(
                f"crews || success: {success_saves} | failed: {failed_saves}"
            )
        )

    def set_cast_photos(self):
        success_saves = 0
        failed_saves = 0

        for cast in Cast.objects.all():
            try:
                cast.image = f"people/casts/{cast.en_name.replace(' ', '_')}.png"
                cast.save(update_fields=["image"])
                success_saves += 1
            except Exception as e:
                failed_saves += 1
                self.stdout.write(self.style.ERROR(f"{cast.en_name} failed"))
                self.stdout.write(self.style.ERROR(f"error: {e}"))

        self.stdout.write(
            self.style.SUCCESS(
                f"casts || success: {success_saves} | failed: {failed_saves}"
            )
        )

    def set_movie_photos(self):
        success_saves = 0
        failed_saves = 0

        for movie in Movie.objects.all():
            try:
                name = movie.orj_title.replace(" ", "_").replace(":", "")
                movie.poster = f"movies/posters/{name}.png"
                movie.backdrop = f"movies/backdrops/{name}.png"
                movie.save(update_fields=["poster", "backdrop"])
                success_saves += 1
            except Exception as e:
                failed_saves += 1
                self.stdout.write(self.style.ERROR(f"{movie.orj_title} failed"))
                self.stdout.write(self.style.ERROR(f"error: {e}"))

        self.stdout.write(
            self.style.SUCCESS(
                f"movies || success: {success_saves} | failed: {failed_saves}"
            )
        )
