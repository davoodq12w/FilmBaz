from django.db import models
from account.models import FilmBazUser
from film.models import Movie, MovieEpisode


class Interaction(models.Model):
    class Type(models.TextChoices):
        VIEW = 'view', 'View' # 0.2
        LIKE = 'like', 'Like' # 1.0
        SAVE = 'save', 'Save' # 1.5
        COMMENT = 'comment', 'Comment' # 0.5
        SHARE = 'share', 'Share' # 1.2
        SEARCH = 'search', 'Search'# 0.1
        WATCH = 'watch', 'Watch' # 0.7
        COMPLETE = 'complete', 'Complete' # 1.2

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

