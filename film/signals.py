from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django_redis import get_redis_connection
from .models import Movie


@receiver(post_save, sender=Movie)
@receiver(post_delete, sender=Movie)
def clear_movie_cache_after_change(sender, instance, **kwargs):
    conn = get_redis_connection("default")
    conn.delete_pattern("bmv:qs:*:Movie:*")
    conn.delete_pattern(f"bmv:obj:*:Movie:{instance.pk}")
