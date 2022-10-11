from rest_framework import serializers

from django.utils.translation import ugettext_lazy as _
from django.contrib.auth import get_user_model


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ['id', 'first_name', 'last_name', 'email', 'password']
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