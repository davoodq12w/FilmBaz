from django.core.validators import FileExtensionValidator
from django.db import models
from django_resized import ResizedImageField
from account.models import FilmBazUser


# Create your models here.
class Genre(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)

    class Meta:
        ordering = ['name']
        indexes = [
            models.Index(fields=['name']),
        ]

    def __str__(self):
        return self.name


def image_sorter(instance, filename):
    return f"movies/{instance.year}/{instance.title}/{filename}"


class Movie(models.Model):
    # ----------------------------------------------------------------
    thumbnail = ResizedImageField(upload_to=image_sorter, size=[300, 400], crop=["middle", "center"], quality=100)
    trailer = models.FileField(upload_to=image_sorter, validators=[
        FileExtensionValidator(allowed_extensions=['MOV', 'avi', 'mp4', 'webm', 'mkv'])])
    # ----------------------------------------------------------------
    title = models.CharField(max_length=200)
    english_title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200)
    description = models.TextField(max_length=2000)
    rate = models.FloatField(default=5)
    year = models.CharField(max_length=4)
    country = models.CharField(max_length=200)
    # ----------------------------------------------------------------
    users_saved = models.ManyToManyField(FilmBazUser, related_name="saves", blank=True)
    # ----------------------------------------------------------------
    is_dubbed = models.BooleanField(default=False)
    # ----------------------------------------------------------------
    genres = models.ManyToManyField(Genre, related_name="movies")
    # ----------------------------------------------------------------
    director = models.CharField(max_length=200)
    producer = models.CharField(max_length=200, blank=True, null=True)
    composer = models.CharField(max_length=200, blank=True, null=True)
    editor = models.CharField(max_length=200, blank=True, null=True)
    # ----------------------------------------------------------------
    created = models.DateField(auto_now_add=True)

    class Meta:
        ordering = ['-created']
        indexes = [
            models.Index(fields=['-created']),
        ]

    def __str__(self):
        return f"{self.title} - {self.year}"


def file_sorter(instance, filename):
    return f"movies/{instance.movie.year}/{instance.movie.title}/{instance.title}/{filename}"


class File(models.Model):
    movie = models.ForeignKey(Movie, related_name="files", on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    description = models.CharField(max_length=500, blank=True, null=True)
    file = models.FileField(upload_to=file_sorter, validators=[
        FileExtensionValidator(allowed_extensions=['MOV', 'avi', 'mp4', 'webm', 'mkv'])])


class Cast(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200)
    movies = models.ManyToManyField(Movie, related_name="casts")
    image = ResizedImageField(upload_to="casts/", quality=50, crop=["middle", "center"], size=[200, 200])

    class Meta:
        ordering = ['name']
        indexes = [
            models.Index(fields=['name']),
        ]

    def __str__(self):
        return self.name


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
