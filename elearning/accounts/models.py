from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    """Extends Django's built-in user with a role and profile fields (R1a, R3)."""

    class Role(models.TextChoices):
        STUDENT = 'student', 'Student'
        TEACHER = 'teacher', 'Teacher'

    role = models.CharField(max_length=10, choices=Role.choices, default=Role.STUDENT)
    real_name = models.CharField(max_length=150, blank=True)
    photo = models.ImageField(upload_to='profile_photos/', blank=True, null=True)
    bio = models.TextField(blank=True)

    def is_teacher(self):
        return self.role == self.Role.TEACHER

    def is_student(self):
        return self.role == self.Role.STUDENT

    def __str__(self):
        return self.real_name or self.username


class StatusUpdate(models.Model):
    """A short post a user shares on their home page feed (R1i)."""

    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='status_updates')
    content = models.CharField(max_length=280)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.user}: {self.content[:30]}'
