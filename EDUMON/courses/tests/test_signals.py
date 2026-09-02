from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase

from accounts.models import CustomUser
from courses.models import Course, CourseMaterial, Enrolment
from notifications.models import Notification


def make_teacher(username='teacher1'):
    return CustomUser.objects.create_user(username=username, password='pass12345', role=CustomUser.Role.TEACHER)


def make_student(username='student1'):
    return CustomUser.objects.create_user(username=username, password='pass12345', role=CustomUser.Role.STUDENT)


class EnrolmentSignalTests(TestCase):
    def test_enrolling_notifies_teacher(self):
        teacher = make_teacher()
        student = make_student()
        course = Course.objects.create(title='Web Dev', teacher=teacher)

        Enrolment.objects.create(student=student, course=course)

        notification = Notification.objects.get(recipient=teacher)
        self.assertIn(student.username, notification.verb)
        self.assertIn(course.title, notification.verb)

    def test_re_saving_enrolment_does_not_duplicate_notification(self):
        teacher = make_teacher()
        student = make_student()
        course = Course.objects.create(title='Web Dev', teacher=teacher)
        enrolment = Enrolment.objects.create(student=student, course=course)

        enrolment.is_blocked = True
        enrolment.save()

        self.assertEqual(Notification.objects.filter(recipient=teacher).count(), 1)


class MaterialSignalTests(TestCase):
    def test_new_material_notifies_enrolled_unblocked_students(self):
        teacher = make_teacher()
        active_student = make_student('active')
        blocked_student = make_student('blocked')
        course = Course.objects.create(title='Web Dev', teacher=teacher)
        Enrolment.objects.create(student=active_student, course=course)
        Enrolment.objects.create(student=blocked_student, course=course, is_blocked=True)

        CourseMaterial.objects.create(
            course=course, title='Slides', file=SimpleUploadedFile('slides.pdf', b'x')
        )

        self.assertTrue(Notification.objects.filter(recipient=active_student).exists())
        self.assertFalse(Notification.objects.filter(recipient=blocked_student).exists())

    def test_no_students_means_no_notifications(self):
        teacher = make_teacher()
        course = Course.objects.create(title='Web Dev', teacher=teacher)

        CourseMaterial.objects.create(
            course=course, title='Slides', file=SimpleUploadedFile('slides.pdf', b'x')
        )

        self.assertEqual(Notification.objects.count(), 0)
