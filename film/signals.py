from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django_redis import get_redis_connection
from .models import Movie, Comment


@receiver(post_save, sender=Movie)
@receiver(post_delete, sender=Movie)
def clear_movie_cache_after_change(sender, instance, **kwargs):
    conn = get_redis_connection("default")
    conn.delete_pattern("movies_list_*")
    conn.delete_pattern(f"movie_detail_*")


@receiver(post_save, sender=Comment)
@receiver(post_delete, sender=Comment)
def clear_movie_cache_after_change(sender, instance, **kwargs):
    conn = get_redis_connection("default")
    movie = instance.movie
    conn.delete_pattern(f"movie_comments_{movie.id}_{movie.slug}")
