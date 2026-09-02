from asgiref.sync import sync_to_async
from channels.routing import URLRouter
from channels.testing import WebsocketCommunicator
from django.contrib.auth import get_user_model
from django.test import TransactionTestCase

from chat.models import ChatRoom, Message
from chat.routing import websocket_urlpatterns

User = get_user_model()


class ChatConsumerTests(TransactionTestCase):
    async def _connect(self, user, room_name):
        application = URLRouter(websocket_urlpatterns)
        communicator = WebsocketCommunicator(application, f'/ws/chat/{room_name}/')
        communicator.scope['url_route'] = {'kwargs': {'room_name': room_name}}
        communicator.scope['user'] = user
        connected, _ = await communicator.connect()
        return communicator, connected

    async def test_two_users_exchange_messages_live(self):
        alice = await self._create_user('alice')
        bob = await self._create_user('bob')
        await self._make_room_with_participants('general', [alice, bob])

        alice_comm, alice_connected = await self._connect(alice, 'general')
        bob_comm, bob_connected = await self._connect(bob, 'general')
        self.assertTrue(alice_connected)
        self.assertTrue(bob_connected)

        await alice_comm.send_json_to({'message': 'hello bob'})

        alice_echo = await alice_comm.receive_json_from()
        bob_received = await bob_comm.receive_json_from()
        self.assertEqual(alice_echo['message'], 'hello bob')
        self.assertEqual(bob_received['username'], 'alice')
        self.assertEqual(bob_received['message'], 'hello bob')

        await alice_comm.disconnect()
        await bob_comm.disconnect()

        message_exists = await self._message_exists('general', 'hello bob')
        self.assertTrue(message_exists)

    async def test_non_participant_is_rejected(self):
        alice = await self._create_user('alice2')
        bob = await self._create_user('bob2')
        carol = await self._create_user('carol2')
        await self._make_room_with_participants('private-room', [alice, bob])

        communicator, connected = await self._connect(carol, 'private-room')
        self.assertFalse(connected)

    @staticmethod
    @sync_to_async
    def _create_user(username):
        return User.objects.create_user(username=username, password='pass12345')

    @staticmethod
    @sync_to_async
    def _make_room_with_participants(name, users):
        room = ChatRoom.objects.create(name=name)
        room.participants.add(*users)
        return room

    @staticmethod
    @sync_to_async
    def _message_exists(room_name, body):
        return Message.objects.filter(room__name=room_name, body=body).exists()
