from django.db import models
from account.models import FilmBazUser
from film.models import Movie


class Interaction(models.Model):
    class Type(models.TextChoices):
        VIEW = 'view', 'View'
        LIKE = 'like', 'Like'
        SAVE = 'save', 'Save'
        COMMENT = 'comment', 'Comment'
        SHARE = 'share', 'Share'
        SEARCH = 'search', 'Search'

    user = models.ForeignKey(
        FilmBazUser, on_delete=models.CASCADE, related_name='interactions'
    )
    movie = models.ForeignKey(
        Movie, on_delete=models.CASCADE, related_name='interactions',
        null=True, blank=True
    )
    interaction_type = models.CharField(
        max_length=10, choices=Type.choices
    )
    weight = models.FloatField(
        help_text="وزن عددی هر نوع تعامل برای مدل CF"
    )
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=['user', 'movie']),
            models.Index(fields=['interaction_type']),
        ]
