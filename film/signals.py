from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.core.cache import cache
from .models import Movie, Comment


@receiver(post_save, sender=Movie)
@receiver(post_delete, sender=Movie)
def clear_movie_cache_after_change(sender, instance, **kwargs):
    try:
        cache.delete_pattern("movies_list_*")
        cache.delete_pattern(f"movie_detail_*")
    except Exception as e:
        print(e)


@receiver(post_save, sender=Comment)
@receiver(post_delete, sender=Comment)
def clear_comments_cache_after_change(sender, instance, **kwargs):
    try:
        movie = instance.movie
        cache.delete_pattern(f"movie_comments_{movie.id}_{movie.slug}")
    except Exception as e:
        print(e)
