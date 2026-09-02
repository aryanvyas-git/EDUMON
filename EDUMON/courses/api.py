from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Course, Enrolment
from .permissions import IsCourseOwnerOrReadOnly, IsTeacherOrReadOnly
from .serializers import CourseSerializer, EnrolmentSerializer, FeedbackSerializer


class CourseViewSet(viewsets.ModelViewSet):
    """Course CRUD plus self-enrolment and feedback endpoints (R1d–R1f, R4)."""

    queryset = Course.objects.select_related('teacher').all()
    serializer_class = CourseSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['teacher']

    def get_permissions(self):
        if self.action in ('create', 'update', 'partial_update', 'destroy'):
            classes = [permissions.IsAuthenticated, IsTeacherOrReadOnly, IsCourseOwnerOrReadOnly]
        else:
            classes = [permissions.IsAuthenticated]
        return [permission() for permission in classes]

    def perform_create(self, serializer):
        serializer.save(teacher=self.request.user)

    @action(detail=True, methods=['post'])
    def enrol(self, request, pk=None):
        """Student self-enrolment on this course (R1e)."""
        course = self.get_object()
        if not request.user.is_student():
            return Response({'detail': 'Only students can enrol.'}, status=status.HTTP_403_FORBIDDEN)
        enrolment, created = Enrolment.objects.get_or_create(student=request.user, course=course)
        serializer = EnrolmentSerializer(enrolment)
        code = status.HTTP_201_CREATED if created else status.HTTP_200_OK
        return Response(serializer.data, status=code)

    @action(detail=True, methods=['get', 'post'])
    def feedback(self, request, pk=None):
        """List course feedback or let an enrolled, unblocked student post some (R1f)."""
        course = self.get_object()
        if request.method == 'GET':
            serializer = FeedbackSerializer(course.feedback.all(), many=True)
            return Response(serializer.data)

        enrolment = Enrolment.objects.filter(course=course, student=request.user, is_blocked=False).first()
        if not enrolment:
            return Response(
                {'detail': 'Only enrolled, unblocked students can leave feedback.'},
                status=status.HTTP_403_FORBIDDEN,
            )
        serializer = FeedbackSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(course=course, student=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
