from django.db.models.signals import post_save
from django.dispatch import receiver

from notifications.models import Notification
from notifications.utils import push_notification

from .models import CourseMaterial, Enrolment


@receiver(post_save, sender=Enrolment)
def notify_teacher_on_enrolment(sender, instance, created, **kwargs):
    """Notify the course teacher when a student enrols (R1k)."""
    if not created:
        return
    notification = Notification.objects.create(
        recipient=instance.course.teacher,
        verb=f'{instance.student} enrolled on {instance.course.title}',
        target=f'course:{instance.course_id}',
    )
    push_notification(notification)


@receiver(post_save, sender=CourseMaterial)
def notify_students_on_new_material(sender, instance, created, **kwargs):
    """Notify enrolled, non-blocked students when new material is added (R1l)."""
    if not created:
        return
    student_ids = Enrolment.objects.filter(
        course=instance.course, is_blocked=False
    ).values_list('student_id', flat=True)
    for student_id in student_ids:
        notification = Notification.objects.create(
            recipient_id=student_id,
            verb=f'New material "{instance.title}" added to {instance.course.title}',
            target=f'course:{instance.course_id}',
        )
        push_notification(notification)
