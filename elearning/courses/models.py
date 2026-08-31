from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class Course(models.Model):
    """A course created and managed by a teacher (R1d)."""

    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    teacher = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='courses_taught',
        limit_choices_to={'role': 'teacher'},
    )
    students = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        through='Enrolment',
        related_name='courses_enrolled',
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title


class Enrolment(models.Model):
    """Through-model linking a student to a course (R1e), enabling blocking (R1h)."""

    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='enrolments',
        limit_choices_to={'role': 'student'},
    )
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='enrolments')
    enrolled_at = models.DateTimeField(auto_now_add=True)
    is_blocked = models.BooleanField(default=False)

    class Meta:
        unique_together = ('student', 'course')
        ordering = ['-enrolled_at']

    def __str__(self):
        status = ' (blocked)' if self.is_blocked else ''
        return f'{self.student} in {self.course}{status}'


class Feedback(models.Model):
    """Rating and comment a student leaves on a course they are enrolled in (R1f)."""

    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='feedback')
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='feedback_given',
    )
    rating = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('course', 'student')
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.student} rated {self.course}: {self.rating}/5'


class CourseMaterial(models.Model):
    """A file a teacher uploads for a course (R1j)."""

    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='materials')
    title = models.CharField(max_length=200)
    file = models.FileField(upload_to='course_materials/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-uploaded_at']

    def __str__(self):
        return f'{self.title} ({self.course})'
