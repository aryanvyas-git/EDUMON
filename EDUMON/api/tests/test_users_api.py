from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase

from accounts.models import CustomUser


class UserApiTests(APITestCase):
    def setUp(self):
        self.teacher = CustomUser.objects.create_user(
            username='teacher1', password='pass12345', role=CustomUser.Role.TEACHER
        )
        self.student = CustomUser.objects.create_user(
            username='student1', password='pass12345', role=CustomUser.Role.STUDENT
        )

    def test_list_requires_authentication(self):
        response = self.client.get(reverse('api:user-list'))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_teacher_can_list_users(self):
        self.client.force_authenticate(self.teacher)
        response = self.client.get(reverse('api:user-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_student_cannot_list_users(self):
        self.client.force_authenticate(self.student)
        response = self.client.get(reverse('api:user-list'))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_any_authenticated_user_can_retrieve_a_profile(self):
        self.client.force_authenticate(self.student)
        response = self.client.get(reverse('api:user-detail', args=[self.teacher.pk]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], 'teacher1')

    def test_user_can_update_own_profile(self):
        self.client.force_authenticate(self.student)
        response = self.client.patch(
            reverse('api:user-detail', args=[self.student.pk]), {'bio': 'Updated bio'}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.student.refresh_from_db()
        self.assertEqual(self.student.bio, 'Updated bio')

    def test_user_cannot_update_others_profile(self):
        self.client.force_authenticate(self.student)
        response = self.client.patch(
            reverse('api:user-detail', args=[self.teacher.pk]), {'bio': 'Hacked'}
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
