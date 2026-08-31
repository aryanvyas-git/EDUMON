from django.core.exceptions import ValidationError
from django.test import TestCase

from accounts.models import CustomUser
from courses.forms import FeedbackForm
from courses.models import Course, Feedback


class FeedbackFormTests(TestCase):
    def test_valid_rating_accepted(self):
        form = FeedbackForm(data={'rating': 3, 'comment': 'Solid course'})
        self.assertTrue(form.is_valid())

    def test_rating_out_of_range_fails_model_validation(self):
        teacher = CustomUser.objects.create_user(username='t', password='pass12345', role=CustomUser.Role.TEACHER)
        student = CustomUser.objects.create_user(username='s', password='pass12345')
        course = Course.objects.create(title='Web Dev', teacher=teacher)
        feedback = Feedback(course=course, student=student, rating=6, comment='Too high')
        with self.assertRaises(ValidationError):
            feedback.full_clean()
