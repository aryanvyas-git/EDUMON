from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand

from accounts.models import CustomUser, StatusUpdate
from chat.models import ChatRoom, Message
from courses.models import Course, CourseMaterial, Enrolment, Feedback


class Command(BaseCommand):
    help = 'Seed the database with demo teachers, students, courses and enrolments.'

    def handle(self, *args, **options):
        if CustomUser.objects.filter(username='admin').exists():
            self.stdout.write(self.style.WARNING('Demo data already loaded — skipping.'))
            return

        CustomUser.objects.create_superuser(
            username='admin', email='admin@example.com', password='adminpass123',
        )

        teachers = [
            CustomUser.objects.create_user(
                username='t_smith', password='teachpass123', email='smith@example.com',
                role=CustomUser.Role.TEACHER, real_name='Dr. Smith', bio='Teaches web development.',
            ),
            CustomUser.objects.create_user(
                username='t_jones', password='teachpass123', email='jones@example.com',
                role=CustomUser.Role.TEACHER, real_name='Prof. Jones', bio='Teaches databases.',
            ),
        ]

        students = [
            CustomUser.objects.create_user(
                username=f's_student{i}', password='studentpass123', email=f'student{i}@example.com',
                role=CustomUser.Role.STUDENT, real_name=f'Student {i}',
            )
            for i in range(1, 6)
        ]

        courses = [
            Course.objects.create(
                title='Advanced Web Development', description='Django, DRF and Channels.', teacher=teachers[0],
            ),
            Course.objects.create(
                title='Database Systems', description='Relational modelling and SQL.', teacher=teachers[1],
            ),
        ]

        for i, student in enumerate(students):
            course = courses[i % len(courses)]
            Enrolment.objects.create(student=student, course=course)
            if i == 0:
                Feedback.objects.create(course=course, student=student, rating=5, comment='Excellent course!')
            StatusUpdate.objects.create(user=student, content=f'{student.real_name} just joined {course.title}.')

        material = CourseMaterial(course=courses[0], title='Week 1 slides')
        material.file.save('week1_slides.txt', ContentFile(b'Welcome to Week 1 of Advanced Web Development.'))

        room = ChatRoom.objects.create(name='general')
        room.participants.add(*students, *teachers)
        Message.objects.create(room=room, sender=teachers[0], body='Welcome to the course chat!')

        self.stdout.write(self.style.SUCCESS(
            'Demo data loaded: 1 admin, 2 teachers, 5 students, 2 courses.\n'
            'Admin login: admin / adminpass123\n'
            'Teacher login: t_smith / teachpass123\n'
            'Student login: s_student1 / studentpass123'
        ))
