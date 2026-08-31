from rest_framework import serializers

from .models import Course, Enrolment, Feedback


class CourseSerializer(serializers.ModelSerializer):
    teacher = serializers.ReadOnlyField(source='teacher.username')

    class Meta:
        model = Course
        fields = ['id', 'title', 'description', 'teacher', 'created_at']
        read_only_fields = ['id', 'teacher', 'created_at']


class EnrolmentSerializer(serializers.ModelSerializer):
    student = serializers.ReadOnlyField(source='student.username')

    class Meta:
        model = Enrolment
        fields = ['id', 'student', 'course', 'enrolled_at', 'is_blocked']
        read_only_fields = ['id', 'student', 'enrolled_at', 'is_blocked']


class FeedbackSerializer(serializers.ModelSerializer):
    student = serializers.ReadOnlyField(source='student.username')

    class Meta:
        model = Feedback
        fields = ['id', 'course', 'student', 'rating', 'comment', 'created_at']
        read_only_fields = ['id', 'course', 'student', 'created_at']
