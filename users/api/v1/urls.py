from django.urls import path

from .views import (
    UserRegisterView,
    UserDetailView,
    ProjectListView,
    ProjectDetailView,
    CustomTokenObtainPairView,
    APIKeyListView,
)


urlpatterns = [
    path('<int:pk>/', UserDetailView.as_view(), name='user-detail'),
    path('register/', UserRegisterView.as_view(), name='user-register'),
    path('token/', CustomTokenObtainPairView.as_view(), name='token-obtain-pair'),

    path('projects/', ProjectListView.as_view(), name='project-list'),
    path('projects/<int:pk>/', ProjectDetailView.as_view(), name='project-list'),

    path('api-keys/', APIKeyListView.as_view(), name='api-keys-list'),
]
