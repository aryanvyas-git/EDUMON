from django.test import TestCase
from django.urls import reverse

from accounts.models import CustomUser
from courses.models import Course, CourseMaterial, Enrolment, Feedback


def make_teacher(username='teacher1'):
    return CustomUser.objects.create_user(username=username, password='pass12345', role=CustomUser.Role.TEACHER)


def make_student(username='student1'):
    return CustomUser.objects.create_user(username=username, password='pass12345', role=CustomUser.Role.STUDENT)


class CourseCreateViewTests(TestCase):
    def test_teacher_can_create_course(self):
        teacher = make_teacher()
        self.client.login(username='teacher1', password='pass12345')
        response = self.client.post(reverse('courses:course_create'), {
            'title': 'Advanced Web Dev',
            'description': 'Django + DRF + Channels',
        })
        self.assertEqual(Course.objects.count(), 1)
        course = Course.objects.first()
        self.assertEqual(course.teacher, teacher)
        self.assertRedirects(response, reverse('courses:course_detail', args=[course.pk]))

    def test_student_cannot_create_course(self):
        make_student()
        self.client.login(username='student1', password='pass12345')
        response = self.client.post(reverse('courses:course_create'), {
            'title': 'Hack', 'description': '',
        })
        self.assertEqual(response.status_code, 403)
        self.assertEqual(Course.objects.count(), 0)


class EnrolmentViewTests(TestCase):
    def setUp(self):
        self.teacher = make_teacher()
        self.student = make_student()
        self.course = Course.objects.create(title='Web Dev', teacher=self.teacher)

    def test_student_can_enrol(self):
        self.client.login(username='student1', password='pass12345')
        response = self.client.post(reverse('courses:enrol', args=[self.course.pk]))
        self.assertRedirects(response, reverse('courses:course_detail', args=[self.course.pk]))
        self.assertTrue(Enrolment.objects.filter(student=self.student, course=self.course).exists())

    def test_teacher_cannot_enrol(self):
        self.client.login(username='teacher1', password='pass12345')
        response = self.client.post(reverse('courses:enrol', args=[self.course.pk]))
        self.assertEqual(response.status_code, 403)

    def test_double_enrol_does_not_duplicate(self):
        Enrolment.objects.create(student=self.student, course=self.course)
        self.client.login(username='student1', password='pass12345')
        self.client.post(reverse('courses:enrol', args=[self.course.pk]))
        self.assertEqual(Enrolment.objects.filter(student=self.student, course=self.course).count(), 1)


class FeedbackViewTests(TestCase):
    def setUp(self):
        self.teacher = make_teacher()
        self.student = make_student()
        self.course = Course.objects.create(title='Web Dev', teacher=self.teacher)
        Enrolment.objects.create(student=self.student, course=self.course)

    def test_enrolled_student_can_leave_feedback(self):
        self.client.login(username='student1', password='pass12345')
        response = self.client.post(reverse('courses:add_feedback', args=[self.course.pk]), {
            'rating': 4, 'comment': 'Good course',
        })
        self.assertRedirects(response, reverse('courses:course_detail', args=[self.course.pk]))
        self.assertTrue(Feedback.objects.filter(course=self.course, student=self.student).exists())

    def test_blocked_student_cannot_leave_feedback(self):
        Enrolment.objects.filter(student=self.student, course=self.course).update(is_blocked=True)
        self.client.login(username='student1', password='pass12345')
        response = self.client.post(reverse('courses:add_feedback', args=[self.course.pk]), {
            'rating': 4, 'comment': 'Good course',
        })
        self.assertEqual(response.status_code, 403)

    def test_non_enrolled_student_cannot_leave_feedback(self):
        other = make_student('student2')
        self.client.login(username='student2', password='pass12345')
        response = self.client.post(reverse('courses:add_feedback', args=[self.course.pk]), {
            'rating': 4, 'comment': 'Good course',
        })
        self.assertEqual(response.status_code, 404)


class MaterialUploadViewTests(TestCase):
    def setUp(self):
        self.teacher = make_teacher()
        self.other_teacher = make_teacher('teacher2')
        self.course = Course.objects.create(title='Web Dev', teacher=self.teacher)

    def test_owning_teacher_can_upload_material(self):
        from django.core.files.uploadedfile import SimpleUploadedFile
        self.client.login(username='teacher1', password='pass12345')
        response = self.client.post(reverse('courses:upload_material', args=[self.course.pk]), {
            'title': 'Lecture 1',
            'file': SimpleUploadedFile('lecture1.pdf', b'content'),
        })
        self.assertRedirects(response, reverse('courses:course_detail', args=[self.course.pk]))
        self.assertTrue(CourseMaterial.objects.filter(course=self.course, title='Lecture 1').exists())

    def test_other_teacher_cannot_upload_material(self):
        self.client.login(username='teacher2', password='pass12345')
        response = self.client.post(reverse('courses:upload_material', args=[self.course.pk]), {
            'title': 'Lecture 1',
        })
        self.assertEqual(response.status_code, 403)


class BlockStudentViewTests(TestCase):
    def setUp(self):
        self.teacher = make_teacher()
        self.student = make_student()
        self.course = Course.objects.create(title='Web Dev', teacher=self.teacher)
        self.enrolment = Enrolment.objects.create(student=self.student, course=self.course)

    def test_teacher_can_block_and_unblock_student(self):
        self.client.login(username='teacher1', password='pass12345')
        url = reverse('courses:toggle_block_student', args=[self.course.pk, self.enrolment.pk])
        self.client.post(url)
        self.enrolment.refresh_from_db()
        self.assertTrue(self.enrolment.is_blocked)

        self.client.post(url)
        self.enrolment.refresh_from_db()
        self.assertFalse(self.enrolment.is_blocked)

    def test_non_owning_teacher_cannot_block_student(self):
        make_teacher('teacher2')
        self.client.login(username='teacher2', password='pass12345')
        url = reverse('courses:toggle_block_student', args=[self.course.pk, self.enrolment.pk])
        response = self.client.post(url)
        self.assertEqual(response.status_code, 403)
