from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from django.utils.translation import ugettext_lazy as _


class ComponentSerializer(serializers.Serializer):
    component_id = serializers.SlugField(default='', allow_blank=True)
    component_type = serializers.SlugField()
    component_inner_text = serializers.CharField(default='', allow_blank=True)

    def validate(self, attrs):
        if not attrs['component_id'] and not attrs['component_inner_text']:
            raise ValidationError(_('Either `component_id` or `component_inner_text` should set'))
        return attrs

    def create(self, validated_data):
        pass

    def update(self, instance, validated_data):
        pass


class LoggerBaseSerializer(serializers.Serializer):
    component = ComponentSerializer(required=False)

    absolute_url = serializers.CharField(default='', allow_blank=True)
    route = serializers.CharField(default='', allow_blank=True)

    client_uuid = serializers.SlugField()
    client_device_type = serializers.ChoiceField(default='', choices=['DESKTOP', 'MOBILE', 'TABLET'], allow_blank=True)
    client_platform = serializers.CharField(default='', allow_blank=True)
    client_public_ip_address = serializers.IPAddressField(default=None, allow_null=True)
    client_os = serializers.CharField(default='', allow_blank=True)
    client_browser = serializers.CharField(default='', allow_blank=True)
    client_browser_version = serializers.CharField(default='', allow_blank=True)
    client_language = serializers.CharField(default='', allow_blank=True)
    client_screen_size = serializers.CharField(default='', allow_blank=True)
    client_document_referrer = serializers.CharField(default='', allow_blank=True)
    client_timezone = serializers.CharField(default='', allow_blank=True)
    client_timezone_offset = serializers.FloatField(default=None, allow_null=True)
    client_timestamp = serializers.IntegerField()

    def validate(self, attrs):
        attrs['log_type'] = 'COMPONENT' if attrs.get('component') else 'GENERAL'
        return attrs


class LoggerLoadCompleteSerializer(LoggerBaseSerializer):
    def create(self, validated_data):
        pass

    def update(self, instance, validated_data):
        pass


class LoggerRateSerializer(LoggerBaseSerializer):
    client_rate = serializers.ChoiceField(choices=[1, 2, 3, 4, 5])
    client_comment = serializers.CharField(default='')

    def create(self, validated_data):
        pass

    def update(self, instance, validated_data):
        pass
