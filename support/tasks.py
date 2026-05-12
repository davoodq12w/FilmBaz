from celery import shared_task
from .models import SupportMessage, SupportSession
from channels.layers import get_channel_layer
import json
from asgiref.sync import async_to_sync


@shared_task()
def send_message_to_chat(message_id):
    message = SupportMessage.objects.filter(id=message_id).first()
    if not message:
        return

    channel_layer = get_channel_layer()

    message_data = {
        "type": "support_chat_message",
        "session_id": message.session_id,
        "user_id": message.session.user.id,
        "support_id": message.session.supporter.id if message.session.supporter else None,
        "message_id": message.id,
        "message_text": message.text,
        "message_timestamp": message.created_at,
        "message_is_seen": message.is_seen,
    }

    data = json.loads(json.dumps(message_data, default=str))
    async_to_sync(channel_layer.group_send)(f'user_session_{message_data["session_id"]}', data)


@shared_task()
def close_support_session_daily():
    objs = SupportSession.objects.all()
    for obj in objs:
        obj.status = SupportSession.Status.CLOSED
        obj.save()
