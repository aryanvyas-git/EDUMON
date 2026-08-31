from django.urls import path

from . import views

app_name = 'accounts'

urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', views.EmailAwareLoginView.as_view(), name='login'),
    path('logout/', views.CustomLogoutView.as_view(), name='logout'),
    path('', views.home, name='home'),
    path('search/', views.search, name='search'),
    path('user/<str:username>/', views.user_detail, name='user_detail'),
]
