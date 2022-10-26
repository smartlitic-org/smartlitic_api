from rest_framework import serializers

from django.utils.translation import ugettext_lazy as _
from django.utils.text import slugify
from django.contrib.auth import get_user_model

from users.models import Project


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ['id', 'email', 'password']
        read_only_fields = ['id']
        extra_kwargs = {
            'password': {'write_only': True}
        }
    
    def create(self, validated_data):
        password = validated_data.pop('password')
        user = get_user_model().objects.create_user(**validated_data)
        user.set_password(password)
        user.save()
        return user

    def update(self, instance, validated_data):
        validated_data.pop('email')  # Will not allow user to change his/her username (email)

        password = validated_data.pop('password')
        if password:
            instance.set_password(password)
        return super().update(instance, validated_data)


class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = ['id', 'project_uuid', 'name', 'slug', 'description', 'website', 'is_enable']
        read_only_fields = ['id', 'project_uuid', 'slug']

    def create(self, validated_data):
        validated_data.update(
            user=self.context['user'],
            slug=slugify(validated_data['name'], allow_unicode=True),
        )
        return super().create(validated_data)

    def update(self, instance, validated_data):
        name = validated_data.get('name')
        if name:
            validated_data.update(
                slug=slugify(name),
            )
        return super().update(instance, validated_data)
