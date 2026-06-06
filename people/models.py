from django.db import models
from film.models import Movie
from django_resized import ResizedImageField

class Cast(models.Model):
    fa_name = models.CharField(max_length=200)
    en_name = models.CharField(max_length=200)
    slug = models.SlugField(
        max_length=200,
        unique=True,
        db_index=True
    )

    image = ResizedImageField(
        upload_to="people/casts/",
        quality=50,
        crop=["middle", "center"],
        size=[200, 200],
        null=True,
        blank=True
    )

    movies = models.ManyToManyField(
        Movie,
        related_name="casts",
        blank=True
    )

    class Meta:
        ordering = ["en_name"]

    def __str__(self):
        return self.en_name
class CrewMember(models.Model):
    fa_name = models.CharField(max_length=200)
    en_name = models.CharField(max_length=200)
    slug = models.SlugField(
        max_length=200,
        unique=True,
        db_index=True
    )

    image = ResizedImageField(
        upload_to="people/crews/",
        quality=50,
        crop=["middle", "center"],
        size=[200, 200],
        null=True,
        blank=True
    )

    class Meta:
        ordering = ["en_name"]

    def __str__(self):
        return self.en_name

class MovieCrew(models.Model):

    class CrewRole(models.TextChoices):
        DIRECTOR = "director", "Director"
        PRODUCER = "producer", "Producer"
        WRITER = "writer", "Writer"

    movie = models.ForeignKey(
        Movie,
        on_delete=models.CASCADE,
        related_name="movie_crews"
    )

    crew = models.ForeignKey(
        CrewMember,
        on_delete=models.CASCADE,
        related_name="movie_crews"
    )

    role = models.CharField(
        max_length=20,
        choices=CrewRole.choices
    )

    class Meta:
        unique_together = (
            "movie",
            "crew",
            "role"
        )

    def __str__(self):
        return f"{self.movie} - {self.crew} ({self.role})"