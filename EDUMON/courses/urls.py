from django.urls import path

from . import views

app_name = 'courses'

urlpatterns = [
    path('', views.course_list, name='course_list'),
    path('new/', views.course_create, name='course_create'),
    path('<int:pk>/', views.course_detail, name='course_detail'),
    path('<int:pk>/enrol/', views.enrol, name='enrol'),
    path('<int:pk>/feedback/', views.add_feedback, name='add_feedback'),
    path('<int:pk>/materials/upload/', views.upload_material, name='upload_material'),
    path('<int:pk>/students/', views.manage_students, name='manage_students'),
    path('<int:pk>/students/<int:enrolment_id>/toggle-block/', views.toggle_block_student, name='toggle_block_student'),
]
