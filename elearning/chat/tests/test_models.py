from django.test import TestCase

from accounts.models import CustomUser
from chat.models import ChatRoom, Message


class ChatModelTests(TestCase):
    def test_room_str_is_name(self):
        room = ChatRoom.objects.create(name='dm-alice-bob')
        self.assertEqual(str(room), 'dm-alice-bob')

    def test_messages_ordered_oldest_first(self):
        user = CustomUser.objects.create_user(username='alice', password='pass12345')
        room = ChatRoom.objects.create(name='general')
        first = Message.objects.create(room=room, sender=user, body='hi')
        second = Message.objects.create(room=room, sender=user, body='there')
        self.assertEqual(list(room.messages.all()), [first, second])
