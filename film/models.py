from django.db import models
from django_resized import ResizedImageField
from account.models import FilmBazUser
from django.utils.text import slugify


class Genre(models.Model):
    fa_name = models.CharField(max_length=200)
    en_name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)

    class Meta:
        ordering = ['en_name']
        indexes = [
            models.Index(fields=['en_name']),
        ]

    def __str__(self):
        return f"{self.en_name}/{self.fa_name}"


def image_sorter(instance, filename):
    year = instance.release_date or "unknown"
    title = slugify(instance.title) or "unknown"

    return f"movies/{year}/{title}/{filename}"


class Movie(models.Model):
    # ----------------------------------------------------------------
    poster = ResizedImageField(upload_to=image_sorter, size=[300, 400], crop=["middle", "center"], quality=100,
                               null=True, blank=True)
    backdrop = ResizedImageField(upload_to=image_sorter, size=[1600, 900], crop=["middle", "center"], quality=100,
                                 null=True, blank=True)
    poster_path = models.CharField(max_length=255, null=True, blank=True)
    backdrop_path = models.CharField(max_length=255, null=True, blank=True)
    images_downloaded = models.BooleanField(default=False)
    # ----------------------------------------------------------------
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200)
    description = models.TextField(max_length=2000, null=True, blank=True)
    popularity = models.FloatField(default=0)
    tmdb_rate = models.FloatField(default=0)
    release_date = models.DateField(null=True, blank=True)
    country = models.CharField(max_length=200, null=True, blank=True)
    runtime = models.PositiveSmallIntegerField(null=True, blank=True)
    tmdb_id = models.PositiveIntegerField(unique=True, db_index=True)
    # ----------------------------------------------------------------
    users_saved = models.ManyToManyField(FilmBazUser, related_name="saves", blank=True)
    # ----------------------------------------------------------------
    is_serie = models.BooleanField(default=False)
    adult = models.BooleanField(default=False)
    details_fetched = models.BooleanField(default=False)
    # ----------------------------------------------------------------
    genres = models.ManyToManyField(Genre, related_name="movies")
    # ----------------------------------------------------------------
    created = models.DateField(auto_now_add=True)
    last_tmdb_sync = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created']
        indexes = [
            models.Index(fields=['-created']),
        ]

    def __str__(self):
        return f"{self.title} - {self.year}"

    @property
    def poster_url(self):
        if self.thumbnail:
            return self.thumbnail.url

        if self.poster_path:
            return (
                f"https://image.tmdb.org/t/p/original"
                f"{self.poster_path}"
            )

        return None

    @property
    def backdrop_url(self):
        if self.backdrop:
            return self.backdrop.url

        if self.backdrop_path:
            return (
                f"https://image.tmdb.org/t/p/original"
                f"{self.backdrop_path}"
            )

        return None


class Comment(models.Model):
    text = models.TextField(max_length=300)
    movie = models.ForeignKey(Movie, related_name="comments", on_delete=models.CASCADE)
    user = models.ForeignKey(FilmBazUser, related_name="comments", on_delete=models.CASCADE)

    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created']
        indexes = [
            models.Index(fields=['-created'])
        ]
