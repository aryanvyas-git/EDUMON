from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase

from accounts.models import CustomUser


class SchemaViewTests(APITestCase):
    def test_swagger_ui_loads(self):
        user = CustomUser.objects.create_user(username='alice', password='pass12345')
        self.client.force_authenticate(user)
        response = self.client.get(reverse('api:swagger-ui'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_schema_endpoint_returns_openapi_document(self):
        user = CustomUser.objects.create_user(username='bob', password='pass12345')
        self.client.force_authenticate(user)
        response = self.client.get(reverse('api:schema'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
