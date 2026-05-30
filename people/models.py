from django.db import models
from film.models import Movie
from django_resized import ResizedImageField


class Cast(models.Model):
    fa_name = models.CharField(max_length=200)
    en_name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    movies = models.ManyToManyField(Movie, related_name="casts")
    image = ResizedImageField(upload_to="people/casts/", quality=50, crop=["middle", "center"], size=[200, 200])

    class Meta:
        ordering = ['en_name']
        indexes = [
            models.Index(fields=['en_name']),
        ]

    def __str__(self):
        return f"{self.en_name}/{self.fa_name}"


class CrewMember(models.Model):
    class CrewRole(models.TextChoices):
        DIRECTOR = "director", "Director"  # کارگردان
        PRODUCER = "producer", "Producer"  # تهیه کننده
        WRITER = "writer", "Writer"  # نویسنده
        CINEMATOGRAPHER = "cinematographer", "Cinematographer"  # فیلمبردار
        EDITOR = "editor", "Editor"  # تدوینگر
        COMPOSER = "composer", "Composer"  # آهنگساز

    fa_name = models.CharField(max_length=200)
    en_name = models.CharField(max_length=200)
    role = models.CharField(max_length=50, choices=CrewRole.choices)
    slug = models.SlugField(max_length=200, unique=True)
    movies = models.ManyToManyField(Movie, related_name="crews")
    image = ResizedImageField(upload_to="people/crews/", quality=50, crop=["middle", "center"], size=[200, 200])

    class Meta:
        ordering = ['en_name']
        indexes = [
            models.Index(fields=['en_name']),
        ]

    def __str__(self):
        return f"{self.en_name}/{self.fa_name}"
