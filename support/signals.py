from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import SupportMessage
from .tasks import send_message_to_chat


@receiver(post_save, sender=SupportMessage)
def send_message_to_chat_signal(sender, instance, created, **kwargs):
    if created:
        send_message_to_chat.delay(instance.id)
