from rest_framework.generics import (
    CreateAPIView,
    ListCreateAPIView,
    RetrieveUpdateAPIView,
    RetrieveUpdateDestroyAPIView,
)
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated

from django.contrib.auth import get_user_model

from users.models import Project

from .serializers import UserSerializer, ProjectSerializer


class UserRegisterView(CreateAPIView):
    serializer_class = UserSerializer


class UserDetailView(RetrieveUpdateAPIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = UserSerializer

    def get_queryset(self):
        return get_user_model().objects.filter(id=self.request.user.id)


class ProjectListView(ListCreateAPIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = ProjectSerializer

    def perform_create(self, serializer):
        serializer.context['user'] = self.request.user
        return super().perform_create(serializer)

    def get_queryset(self):
        return Project.available_objects.filter(user=self.request.user)


class ProjectDetailView(RetrieveUpdateDestroyAPIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = ProjectSerializer

    def get_queryset(self):
        return Project.available_objects.filter(user=self.request.user)
