from django.contrib.auth.models import AnonymousUser
from django.test import RequestFactory, TestCase

from accounts.models import CustomUser
from notifications.context_processors import unread_notifications
from notifications.models import Notification


class UnreadNotificationsContextProcessorTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = CustomUser.objects.create_user(username='alice', password='pass12345')

    def test_counts_only_unread_for_authenticated_user(self):
        Notification.objects.create(recipient=self.user, verb='a', is_read=False)
        Notification.objects.create(recipient=self.user, verb='b', is_read=True)
        request = self.factory.get('/')
        request.user = self.user
        self.assertEqual(unread_notifications(request)['unread_notification_count'], 1)

    def test_zero_for_anonymous_user(self):
        request = self.factory.get('/')
        request.user = AnonymousUser()
        self.assertEqual(unread_notifications(request)['unread_notification_count'], 0)
