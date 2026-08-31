import json

from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer

from .models import ChatRoom, Message


class ChatConsumer(AsyncWebsocketConsumer):
    """Joins a Redis-backed group per room, broadcasts and persists messages (R1g)."""

    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.group_name = f'chat_{self.room_name}'
        user = self.scope['user']

        if not user.is_authenticated:
            await self.close()
            return

        room, created = await self._get_or_create_room(self.room_name)
        if not created and not await self._is_participant(room, user):
            await self.close()
            return
        await self._add_participant(room, user)

        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        if hasattr(self, 'group_name'):
            await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        body = data.get('message', '').strip()
        if not body:
            return

        user = self.scope['user']
        await self._save_message(self.room_name, user, body)

        await self.channel_layer.group_send(self.group_name, {
            'type': 'chat.message',
            'username': user.username,
            'message': body,
        })

    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            'username': event['username'],
            'message': event['message'],
        }))

    @database_sync_to_async
    def _get_or_create_room(self, room_name):
        return ChatRoom.objects.get_or_create(name=room_name)

    @database_sync_to_async
    def _is_participant(self, room, user):
        return room.participants.filter(pk=user.pk).exists()

    @database_sync_to_async
    def _add_participant(self, room, user):
        room.participants.add(user)

    @database_sync_to_async
    def _save_message(self, room_name, user, body):
        room = ChatRoom.objects.get(name=room_name)
        Message.objects.create(room=room, sender=user, body=body)
