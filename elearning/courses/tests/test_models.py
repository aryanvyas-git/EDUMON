from django.db import IntegrityError
from django.test import TestCase

from accounts.models import CustomUser
from courses.models import Course, Enrolment, Feedback


def make_teacher(username='teacher1'):
    return CustomUser.objects.create_user(username=username, password='pass12345', role=CustomUser.Role.TEACHER)


def make_student(username='student1'):
    return CustomUser.objects.create_user(username=username, password='pass12345', role=CustomUser.Role.STUDENT)


class CourseModelTests(TestCase):
    def test_str_returns_title(self):
        teacher = make_teacher()
        course = Course.objects.create(title='Web Dev', teacher=teacher)
        self.assertEqual(str(course), 'Web Dev')


class EnrolmentModelTests(TestCase):
    def test_unique_enrolment_per_student_course(self):
        teacher = make_teacher()
        student = make_student()
        course = Course.objects.create(title='Web Dev', teacher=teacher)
        Enrolment.objects.create(student=student, course=course)
        with self.assertRaises(IntegrityError):
            Enrolment.objects.create(student=student, course=course)

    def test_str_shows_blocked_state(self):
        teacher = make_teacher()
        student = make_student()
        course = Course.objects.create(title='Web Dev', teacher=teacher)
        enrolment = Enrolment.objects.create(student=student, course=course, is_blocked=True)
        self.assertIn('blocked', str(enrolment))


class FeedbackModelTests(TestCase):
    def test_one_feedback_per_student_per_course(self):
        teacher = make_teacher()
        student = make_student()
        course = Course.objects.create(title='Web Dev', teacher=teacher)
        Feedback.objects.create(course=course, student=student, rating=5, comment='Great')
        with self.assertRaises(IntegrityError):
            Feedback.objects.create(course=course, student=student, rating=3, comment='Again')
