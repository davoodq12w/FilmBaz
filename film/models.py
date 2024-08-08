from django.core.validators import FileExtensionValidator
from django.db import models
from django_resized import ResizedImageField


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
    thumbnail = ResizedImageField(upload_to=image_sorter)
    trailer = models.FileField(upload_to=image_sorter, validators=[
        FileExtensionValidator(allowed_extensions=['MOV', 'avi', 'mp4', 'webm', 'mkv'])])
    # ----------------------------------------------------------------
    title = models.CharField(max_length=200)
    description = models.TextField(max_length=2000)
    rate = models.FloatField(default=5)
    year = models.DateField()
    country = models.CharField(max_length=200)
    # ----------------------------------------------------------------
    is_dubbed = models.BooleanField(default=False)
    # ----------------------------------------------------------------
    genre = models.ManyToManyField(Genre, related_name="movies")
    # ----------------------------------------------------------------
    director = models.CharField(max_length=200)
    producer = models.CharField(max_length=200)
    composer = models.CharField(max_length=200)
    editor = models.CharField(max_length=200)
    # ----------------------------------------------------------------
    created = models.DateField(auto_now_add=True)

    class Meta:
        ordering = ['-created', '-year']
        indexes = [
            models.Index(fields=['-created']),
            models.Index(fields=['-year']),
        ]

    def __str__(self):
        return f"{self.title} - {self.year}"


def file_sorter(instance, filename):
    return f"movies/{instance.movie.year}/{instance.movie.title}/{instance.title}/{filename}"


class File(models.Model):
    movie = models.ForeignKey(Movie, related_name="files", on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    file = models.FileField(upload_to=file_sorter, validators=[
        FileExtensionValidator(allowed_extensions=['MOV', 'avi', 'mp4', 'webm', 'mkv'])])
