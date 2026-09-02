from django.test import TestCase

from accounts.forms import RegistrationForm, StatusUpdateForm
from accounts.models import CustomUser


class RegistrationFormTests(TestCase):
    def test_valid_data_creates_form(self):
        form = RegistrationForm(data={
            'username': 'newuser',
            'email': 'new@example.com',
            'real_name': 'New User',
            'role': CustomUser.Role.STUDENT,
            'bio': '',
            'password1': 'S3curePass!23',
            'password2': 'S3curePass!23',
        })
        self.assertTrue(form.is_valid(), form.errors)

    def test_password_mismatch_is_invalid(self):
        form = RegistrationForm(data={
            'username': 'newuser',
            'email': 'new@example.com',
            'real_name': 'New User',
            'role': CustomUser.Role.STUDENT,
            'bio': '',
            'password1': 'S3curePass!23',
            'password2': 'Different!23',
        })
        self.assertFalse(form.is_valid())
        self.assertIn('password2', form.errors)

    def test_duplicate_email_is_invalid(self):
        CustomUser.objects.create_user(username='existing', password='pass12345', email='dup@example.com')
        form = RegistrationForm(data={
            'username': 'newuser',
            'email': 'dup@example.com',
            'real_name': 'New User',
            'role': CustomUser.Role.STUDENT,
            'bio': '',
            'password1': 'S3curePass!23',
            'password2': 'S3curePass!23',
        })
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)


class StatusUpdateFormTests(TestCase):
    def test_blank_content_is_invalid(self):
        form = StatusUpdateForm(data={'content': ''})
        self.assertFalse(form.is_valid())

    def test_content_over_max_length_is_invalid(self):
        form = StatusUpdateForm(data={'content': 'x' * 281})
        self.assertFalse(form.is_valid())
