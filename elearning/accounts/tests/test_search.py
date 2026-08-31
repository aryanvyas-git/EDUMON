from django.test import TestCase
from django.urls import reverse

from accounts.models import CustomUser


class SearchViewTests(TestCase):
    def setUp(self):
        self.teacher = CustomUser.objects.create_user(
            username='teacher1', password='pass12345', role=CustomUser.Role.TEACHER
        )
        self.student = CustomUser.objects.create_user(
            username='student1', password='pass12345', role=CustomUser.Role.STUDENT, real_name='Alice Smith'
        )

    def test_teacher_can_search(self):
        self.client.login(username='teacher1', password='pass12345')
        response = self.client.get(reverse('accounts:search'), {'q': 'Alice'})
        self.assertEqual(response.status_code, 200)
        self.assertIn(self.student, response.context['results'])

    def test_student_cannot_search(self):
        self.client.login(username='student1', password='pass12345')
        response = self.client.get(reverse('accounts:search'), {'q': 'Alice'})
        self.assertEqual(response.status_code, 403)

    def test_empty_query_returns_no_results(self):
        self.client.login(username='teacher1', password='pass12345')
        response = self.client.get(reverse('accounts:search'))
        self.assertEqual(list(response.context['results']), [])
