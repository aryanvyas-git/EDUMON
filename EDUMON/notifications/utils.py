from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer


def push_notification(notification):
    """Push a notification to the recipient's browser over WebSockets (advanced technique bonus)."""
    channel_layer = get_channel_layer()
    if channel_layer is None:
        return
    async_to_sync(channel_layer.group_send)(
        f'notifications_{notification.recipient_id}',
        {'type': 'notify', 'verb': notification.verb, 'id': notification.id},
    )
