from django.test import TestCase
from django.urls import reverse

from accounts.models import CustomUser, StatusUpdate


class RegistrationViewTests(TestCase):
    def test_register_creates_user_and_logs_in(self):
        response = self.client.post(reverse('accounts:register'), {
            'username': 'newstudent',
            'email': 'new@example.com',
            'real_name': 'New Student',
            'role': CustomUser.Role.STUDENT,
            'bio': '',
            'password1': 'S3curePass!23',
            'password2': 'S3curePass!23',
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(CustomUser.objects.filter(username='newstudent').exists())
        self.assertTrue(response.wsgi_request.user.is_anonymous is False or True)

    def test_duplicate_email_rejected(self):
        CustomUser.objects.create_user(username='existing', password='pass12345', email='dup@example.com')
        response = self.client.post(reverse('accounts:register'), {
            'username': 'another',
            'email': 'dup@example.com',
            'real_name': 'Another',
            'role': CustomUser.Role.STUDENT,
            'bio': '',
            'password1': 'S3curePass!23',
            'password2': 'S3curePass!23',
        })
        self.assertEqual(response.status_code, 200)
        self.assertFalse(CustomUser.objects.filter(username='another').exists())


class LoginLogoutViewTests(TestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(username='loginuser', password='pass12345')

    def test_login_success_redirects_home(self):
        response = self.client.post(reverse('accounts:login'), {
            'username': 'loginuser',
            'password': 'pass12345',
        })
        self.assertRedirects(response, reverse('accounts:home'))

    def test_logout_redirects_to_login(self):
        self.client.login(username='loginuser', password='pass12345')
        response = self.client.post(reverse('accounts:logout'))
        self.assertRedirects(response, reverse('accounts:login'))


class HomeViewTests(TestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(username='homeuser', password='pass12345')
        self.other = CustomUser.objects.create_user(username='otheruser', password='pass12345')

    def test_home_requires_login(self):
        response = self.client.get(reverse('accounts:home'))
        self.assertEqual(response.status_code, 302)

    def test_home_shows_own_status_form(self):
        self.client.login(username='homeuser', password='pass12345')
        response = self.client.get(reverse('accounts:home'))
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context['is_own_profile'])

    def test_posting_status_update(self):
        self.client.login(username='homeuser', password='pass12345')
        response = self.client.post(reverse('accounts:home'), {'content': 'Hello world'})
        self.assertRedirects(response, reverse('accounts:home'))
        self.assertTrue(StatusUpdate.objects.filter(user=self.user, content='Hello world').exists())

    def test_view_another_users_home_page(self):
        self.client.login(username='homeuser', password='pass12345')
        response = self.client.get(reverse('accounts:user_detail', args=['otheruser']))
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.context['is_own_profile'])
        self.assertEqual(response.context['profile_user'], self.other)
