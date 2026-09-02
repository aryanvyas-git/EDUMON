from django.test import TestCase
from django.urls import reverse

from accounts.models import CustomUser
from notifications.models import Notification


class NotificationListViewTests(TestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(username='alice', password='pass12345')
        self.other = CustomUser.objects.create_user(username='bob', password='pass12345')

    def test_only_own_notifications_are_listed(self):
        mine = Notification.objects.create(recipient=self.user, verb='hello')
        Notification.objects.create(recipient=self.other, verb='not mine')

        self.client.login(username='alice', password='pass12345')
        response = self.client.get(reverse('notifications:list'))
        self.assertEqual(list(response.context['notifications']), [mine])

    def test_mark_read(self):
        notification = Notification.objects.create(recipient=self.user, verb='hello')
        self.client.login(username='alice', password='pass12345')
        response = self.client.post(reverse('notifications:mark_read', args=[notification.pk]))
        self.assertRedirects(response, reverse('notifications:list'))
        notification.refresh_from_db()
        self.assertTrue(notification.is_read)

    def test_cannot_mark_others_notification_read(self):
        notification = Notification.objects.create(recipient=self.other, verb='hello')
        self.client.login(username='alice', password='pass12345')
        response = self.client.post(reverse('notifications:mark_read', args=[notification.pk]))
        self.assertEqual(response.status_code, 404)
