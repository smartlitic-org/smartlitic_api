from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from django.utils.translation import ugettext_lazy as _


class DashboardSerializer(serializers.Serializer):
    report_type = serializers.ChoiceField(choices=['custom', 'today'], default='today')
    report_from = serializers.DateField(allow_null=True, required=False)
    report_until = serializers.DateField(allow_null=True, required=False)

    def validate(self, attrs):
        report_from = attrs.get('report_from')
        report_until = attrs.get('report_until')
        if attrs['report_type'] == 'custom' and not report_from and not report_until:
            raise ValidationError(_('Custom report-type should have date range filter'))
        return attrs

    def create(self, validated_data):
        pass

    def update(self, instance, validated_data):
        pass


class DashboardGeneralSerializer(DashboardSerializer):
    pass


class DashboardComponentSerializer(DashboardSerializer):
    component = serializers.CharField()
