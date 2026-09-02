from rest_framework import permissions, viewsets
from rest_framework.filters import SearchFilter

from .models import CustomUser, StatusUpdate
from .permissions import IsOwnerOrReadOnly, IsTeacher
from .serializers import StatusUpdateSerializer, UserSerializer


class UserViewSet(viewsets.ModelViewSet):
    """List/retrieve/update users. Listing (search) is teacher-only (R1c, R4)."""

    queryset = CustomUser.objects.all().order_by('username')
    serializer_class = UserSerializer
    filter_backends = [SearchFilter]
    search_fields = ['username', 'real_name', 'email']
    http_method_names = ['get', 'put', 'patch', 'head', 'options']

    def get_permissions(self):
        if self.action == 'list':
            classes = [permissions.IsAuthenticated, IsTeacher]
        elif self.action in ('update', 'partial_update'):
            classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]
        else:
            classes = [permissions.IsAuthenticated]
        return [permission() for permission in classes]


class StatusUpdateViewSet(viewsets.ModelViewSet):
    """List and create status updates for the home page feed (R1i, R4)."""

    queryset = StatusUpdate.objects.all()
    serializer_class = StatusUpdateSerializer
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ['get', 'post', 'head', 'options']

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
