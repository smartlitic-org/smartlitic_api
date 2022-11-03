from django.urls import path

from rest_framework_simplejwt.views import (
    TokenObtainPairView,
)

from .views import UserRegisterView, UserDetailView, ProjectListView, ProjectDetailView, CustomTokenObtainPairView


urlpatterns = [
    path('<int:pk>/', UserDetailView.as_view(), name='user-detail'),
    path('register/', UserRegisterView.as_view(), name='user-register'),

    path('projects/', ProjectListView.as_view(), name='project-list'),
    path('projects/<int:pk>/', ProjectDetailView.as_view(), name='project-list'),

    path('token/', CustomTokenObtainPairView.as_view(), name='token-obtain-pair'),
]
