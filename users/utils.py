from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

def notify_user(user_id, data: dict):
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        f"user_{user_id}",
        {
            "type": "send_notification",
            "content": data
        }
    )