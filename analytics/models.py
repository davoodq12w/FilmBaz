from django.db import models
from account.models import FilmBazUser
from film.models import Movie, MovieEpisode


class Interaction(models.Model):
    class Type(models.TextChoices):
        VIEW = 'view', 'View'
        LIKE = 'like', 'Like'
        SAVE = 'save', 'Save'
        COMMENT = 'comment', 'Comment'
        SHARE = 'share', 'Share'
        SEARCH = 'search', 'Search'
        WATCH = 'watch', 'Watch'

    user = models.ForeignKey(FilmBazUser, on_delete=models.CASCADE, related_name='interactions')
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name='interactions')
    interaction_type = models.CharField(max_length=10, choices=Type.choices)
    weight = models.FloatField()
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=['user', 'movie']),
            models.Index(fields=['interaction_type']),
        ]

