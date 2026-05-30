from django.core.validators import FileExtensionValidator
from django.db import models
from django_resized import ResizedImageField
from account.models import FilmBazUser


class Category(models.Model):
    fa_name = models.CharField(max_length=200)
    en_name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=100, unique=True)

    class Meta:
        ordering = ['en_name']
        indexes = [
            models.Index(fields=['en_name']),
        ]

    def __str__(self):
        return f"{self.en_name}/{self.fa_name}"


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
    is_serie = models.BooleanField(default=False, null=True, blank=True)
    # ----------------------------------------------------------------
    genres = models.ManyToManyField(Genre, related_name="movies")
    # ----------------------------------------------------------------
    category = models.ManyToManyField(Category, related_name="movies")
    # ----------------------------------------------------------------
    created = models.DateField(auto_now_add=True)

    class Meta:
        ordering = ['-created']
        indexes = [
            models.Index(fields=['-created']),
        ]

    def __str__(self):
        return f"{self.title} - {self.year}"


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
