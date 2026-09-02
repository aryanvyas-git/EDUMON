from django.test import TestCase

from accounts.models import CustomUser
from notifications.models import Notification


class NotificationModelTests(TestCase):
    def test_str_includes_recipient_and_verb(self):
        user = CustomUser.objects.create_user(username='alice', password='pass12345')
        notification = Notification.objects.create(recipient=user, verb='did something')
        self.assertIn('alice', str(notification))
        self.assertIn('did something', str(notification))

    def test_ordering_is_newest_first(self):
        user = CustomUser.objects.create_user(username='alice', password='pass12345')
        first = Notification.objects.create(recipient=user, verb='first')
        second = Notification.objects.create(recipient=user, verb='second')
        self.assertEqual(list(Notification.objects.all()), [second, first])

    def test_defaults_to_unread(self):
        user = CustomUser.objects.create_user(username='alice', password='pass12345')
        notification = Notification.objects.create(recipient=user, verb='hi')
        self.assertFalse(notification.is_read)
