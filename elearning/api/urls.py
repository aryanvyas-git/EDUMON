from django.urls import path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from rest_framework.routers import DefaultRouter

from accounts.api import StatusUpdateViewSet, UserViewSet
from courses.api import CourseViewSet

app_name = 'api'

router = DefaultRouter()
router.register('users', UserViewSet, basename='user')
router.register('statuses', StatusUpdateViewSet, basename='statusupdate')
router.register('courses', CourseViewSet, basename='course')

urlpatterns = router.urls + [
    path('schema/', SpectacularAPIView.as_view(), name='schema'),
    path('schema/swagger-ui/', SpectacularSwaggerView.as_view(url_name='api:schema'), name='swagger-ui'),
]
