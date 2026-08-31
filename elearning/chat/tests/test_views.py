from django.test import TestCase
from django.urls import reverse

from accounts.models import CustomUser
from chat.models import ChatRoom


class StartChatViewTests(TestCase):
    def setUp(self):
        self.alice = CustomUser.objects.create_user(username='alice', password='pass12345')
        self.bob = CustomUser.objects.create_user(username='bob', password='pass12345')

    def test_start_chat_creates_room_with_both_participants(self):
        self.client.login(username='alice', password='pass12345')
        response = self.client.post(reverse('chat:start_chat'), {'user_id': self.bob.pk})
        room = ChatRoom.objects.get(name='dm-alice-bob')
        self.assertRedirects(response, reverse('chat:room_detail', args=[room.name]))
        self.assertIn(self.alice, room.participants.all())
        self.assertIn(self.bob, room.participants.all())

    def test_room_name_is_deterministic_regardless_of_order(self):
        self.client.login(username='bob', password='pass12345')
        self.client.post(reverse('chat:start_chat'), {'user_id': self.alice.pk})
        self.assertTrue(ChatRoom.objects.filter(name='dm-alice-bob').exists())


class RoomDetailViewTests(TestCase):
    def setUp(self):
        self.alice = CustomUser.objects.create_user(username='alice', password='pass12345')
        self.bob = CustomUser.objects.create_user(username='bob', password='pass12345')
        self.carol = CustomUser.objects.create_user(username='carol', password='pass12345')
        self.room = ChatRoom.objects.create(name='dm-alice-bob')
        self.room.participants.add(self.alice, self.bob)

    def test_participant_can_view_room(self):
        self.client.login(username='alice', password='pass12345')
        response = self.client.get(reverse('chat:room_detail', args=[self.room.name]))
        self.assertEqual(response.status_code, 200)

    def test_non_participant_cannot_view_existing_room(self):
        self.client.login(username='carol', password='pass12345')
        response = self.client.get(reverse('chat:room_detail', args=[self.room.name]))
        self.assertEqual(response.status_code, 403)

    def test_visiting_brand_new_room_name_joins_it(self):
        self.client.login(username='carol', password='pass12345')
        response = self.client.get(reverse('chat:room_detail', args=['fresh-room']))
        self.assertEqual(response.status_code, 200)
        self.assertTrue(ChatRoom.objects.get(name='fresh-room').participants.filter(pk=self.carol.pk).exists())
