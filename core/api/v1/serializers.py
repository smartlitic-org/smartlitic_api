from rest_framework import serializers

from core.models import GeneralLog, ComponentLog


class ComponentSerializer(serializers.Serializer):
    component_id = serializers.SlugField()
    component_type = serializers.SlugField()
    component_name = serializers.SlugField()
    component_inner_text = serializers.CharField()

    def create(self, validated_data):
        pass

    def update(self, instance, validated_data):
        pass


class LoggerLoadCompleteSerializer(serializers.Serializer):
    component = ComponentSerializer(required=False)

    absolute_url = serializers.CharField(default='')
    route = serializers.CharField(default='')

    client_uid = serializers.SlugField()
    client_device_type = serializers.ChoiceField(default='', choices=['DESKTOP', 'MOBILE', 'TABLET'])
    client_platform = serializers.CharField(default='')
    client_public_ip_address = serializers.IPAddressField(default=None)
    client_os = serializers.CharField(default='')
    client_browser = serializers.CharField(default='')
    client_browser_version = serializers.CharField(default='')
    client_language = serializers.CharField(default='')
    client_screen_size = serializers.CharField(default='')
    client_document_referrer = serializers.CharField(default='')
    client_timezone = serializers.CharField(default='')
    client_timezone_offset = serializers.CharField(default='')
    client_timestamp = serializers.IntegerField()

    def validate(self, attrs):
        attrs['target_log_model'] = ComponentLog if attrs.get('component') else GeneralLog
        return attrs

    def create(self, validated_data):
        pass

    def update(self, instance, validated_data):
        pass
