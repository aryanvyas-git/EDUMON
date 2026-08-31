from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase

from accounts.models import CustomUser
from accounts.models import StatusUpdate


class StatusUpdateApiTests(APITestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(username='alice', password='pass12345')

    def test_create_status_update_assigns_current_user(self):
        self.client.force_authenticate(self.user)
        response = self.client.post(reverse('api:statusupdate-list'), {'content': 'Hello API'})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        status_update = StatusUpdate.objects.get()
        self.assertEqual(status_update.user, self.user)
        self.assertEqual(status_update.content, 'Hello API')

    def test_list_requires_authentication(self):
        response = self.client.get(reverse('api:statusupdate-list'))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
