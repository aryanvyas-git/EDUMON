from django.test import TestCase

from accounts.models import CustomUser, StatusUpdate


class CustomUserModelTests(TestCase):
    def test_default_role_is_student(self):
        user = CustomUser.objects.create_user(username='alice', password='pass12345')
        self.assertEqual(user.role, CustomUser.Role.STUDENT)
        self.assertTrue(user.is_student())
        self.assertFalse(user.is_teacher())

    def test_teacher_role_helpers(self):
        teacher = CustomUser.objects.create_user(
            username='bob', password='pass12345', role=CustomUser.Role.TEACHER
        )
        self.assertTrue(teacher.is_teacher())
        self.assertFalse(teacher.is_student())

    def test_str_prefers_real_name(self):
        user = CustomUser.objects.create_user(username='carol', password='pass12345', real_name='Carol Danvers')
        self.assertEqual(str(user), 'Carol Danvers')

    def test_str_falls_back_to_username(self):
        user = CustomUser.objects.create_user(username='dave', password='pass12345')
        self.assertEqual(str(user), 'dave')


class StatusUpdateModelTests(TestCase):
    def test_ordering_is_newest_first(self):
        user = CustomUser.objects.create_user(username='erin', password='pass12345')
        first = StatusUpdate.objects.create(user=user, content='first')
        second = StatusUpdate.objects.create(user=user, content='second')
        statuses = list(StatusUpdate.objects.all())
        self.assertEqual(statuses, [second, first])
