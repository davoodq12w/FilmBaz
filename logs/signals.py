from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver
from django.contrib.contenttypes.models import ContentType
from .models import Log
import logs.logging_state as logging_state

MODELS_TO_LOG = [
    'FilmBazUser', 'Ticket', 'Interaction', 'Comment', 'Genre', 'Movie', 'SupportMessage',
    'SupportSession', 'MovieEpisode', 'MovieTrailer', 'WatchProgress',
]


@receiver(post_save)
def log_create_or_update(sender, instance, created, **kwargs):
    """
    Signal receiver to log CREATE or UPDATE actions for specified models.
    """
    if not logging_state.LOGGING_ENABLED:
        return

    if sender.__name__ in MODELS_TO_LOG:
        action = 'CREATE' if created else 'UPDATE'  # Determine if the action is CREATE or UPDATE
        content_type = ContentType.objects.get_for_model(instance)  # Get the content type of the instance
        if sender.__name__ == 'User':
            user = instance
        else:
            user = getattr(instance, 'user', None)

        # Create a log entry
        Log.objects.create(
            user=user,
            action=action,
            content_type=content_type,
            object_id=instance.id,
            details=f"{instance.__class__.__name__} {action}D: {instance}"  # Add details about the action
        )


@receiver(pre_delete)
def log_delete(sender, instance, **kwargs):
    """
    Signal receiver to log DELETE actions for specified models.
    """
    if not logging_state.LOGGING_ENABLED:
        return

    if sender.__name__ in MODELS_TO_LOG:
        content_type = ContentType.objects.get_for_model(instance)  # Get the content type of the instance
        if sender.__name__ == 'User':
            user = instance
        else:
            user = getattr(instance, 'user', None)

        # Create a log entry
        Log.objects.create(
            user=user,
            action='DELETE',
            content_type=content_type,
            object_id=instance.id,
            details=f"{instance.__class__.__name__} DELETED: {instance}"  # Add details about the deletion
        )
