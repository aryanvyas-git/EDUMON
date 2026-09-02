from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase

from accounts.models import CustomUser
from courses.models import Course, Enrolment


def make_teacher(username='teacher1'):
    return CustomUser.objects.create_user(username=username, password='pass12345', role=CustomUser.Role.TEACHER)


def make_student(username='student1'):
    return CustomUser.objects.create_user(username=username, password='pass12345', role=CustomUser.Role.STUDENT)


class CourseApiTests(APITestCase):
    def setUp(self):
        self.teacher = make_teacher()
        self.student = make_student()
        self.course = Course.objects.create(title='Web Dev', teacher=self.teacher)

    def test_list_courses_requires_authentication(self):
        response = self.client.get(reverse('api:course-list'))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_authenticated_user_can_list_courses(self):
        self.client.force_authenticate(self.student)
        response = self.client.get(reverse('api:course-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)

    def test_teacher_can_create_course(self):
        self.client.force_authenticate(self.teacher)
        response = self.client.post(reverse('api:course-list'), {'title': 'New Course', 'description': ''})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Course.objects.count(), 2)

    def test_student_cannot_create_course(self):
        self.client.force_authenticate(self.student)
        response = self.client.post(reverse('api:course-list'), {'title': 'New Course', 'description': ''})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_non_owning_teacher_cannot_update_course(self):
        other_teacher = make_teacher('teacher2')
        self.client.force_authenticate(other_teacher)
        response = self.client.patch(reverse('api:course-detail', args=[self.course.pk]), {'title': 'Hacked'})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_owning_teacher_can_update_course(self):
        self.client.force_authenticate(self.teacher)
        response = self.client.patch(reverse('api:course-detail', args=[self.course.pk]), {'title': 'Renamed'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.course.refresh_from_db()
        self.assertEqual(self.course.title, 'Renamed')


class CourseEnrolApiTests(APITestCase):
    def setUp(self):
        self.teacher = make_teacher()
        self.student = make_student()
        self.course = Course.objects.create(title='Web Dev', teacher=self.teacher)

    def test_student_can_enrol_via_api(self):
        self.client.force_authenticate(self.student)
        response = self.client.post(reverse('api:course-enrol', args=[self.course.pk]))
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Enrolment.objects.filter(student=self.student, course=self.course).exists())

    def test_teacher_cannot_enrol_via_api(self):
        self.client.force_authenticate(self.teacher)
        response = self.client.post(reverse('api:course-enrol', args=[self.course.pk]))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_double_enrol_via_api_is_idempotent(self):
        self.client.force_authenticate(self.student)
        self.client.post(reverse('api:course-enrol', args=[self.course.pk]))
        response = self.client.post(reverse('api:course-enrol', args=[self.course.pk]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Enrolment.objects.filter(student=self.student, course=self.course).count(), 1)


class CourseFeedbackApiTests(APITestCase):
    def setUp(self):
        self.teacher = make_teacher()
        self.student = make_student()
        self.course = Course.objects.create(title='Web Dev', teacher=self.teacher)
        Enrolment.objects.create(student=self.student, course=self.course)

    def test_anyone_authenticated_can_list_feedback(self):
        self.client.force_authenticate(self.teacher)
        response = self.client.get(reverse('api:course-feedback', args=[self.course.pk]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_enrolled_student_can_post_feedback(self):
        self.client.force_authenticate(self.student)
        response = self.client.post(
            reverse('api:course-feedback', args=[self.course.pk]), {'rating': 5, 'comment': 'Great'}
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_non_enrolled_student_cannot_post_feedback(self):
        other = make_student('student2')
        self.client.force_authenticate(other)
        response = self.client.post(
            reverse('api:course-feedback', args=[self.course.pk]), {'rating': 5, 'comment': 'Great'}
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_blocked_student_cannot_post_feedback(self):
        Enrolment.objects.filter(student=self.student, course=self.course).update(is_blocked=True)
        self.client.force_authenticate(self.student)
        response = self.client.post(
            reverse('api:course-feedback', args=[self.course.pk]), {'rating': 5, 'comment': 'Great'}
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
