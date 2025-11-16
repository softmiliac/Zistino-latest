from rest_framework import serializers
from .models import Configuration


class TimeModelSerializer(serializers.Serializer):
    """Serializer for TimeModel structure."""
    start = serializers.CharField(required=False, allow_blank=True, default='')
    end = serializers.CharField(required=False, allow_blank=True, default='')
    split = serializers.CharField(required=False, allow_blank=True, default='')


class ConfigurationSerializer(serializers.ModelSerializer):
    """Serializer for Configuration - matches ConfigModel structure."""
    value = TimeModelSerializer(required=False, allow_null=True)

    class Meta:
        model = Configuration
        fields = ['id', 'name', 'type', 'value']
        read_only_fields = ['id']

    def to_representation(self, instance):
        """Convert value JSON to TimeModel structure."""
        data = super().to_representation(instance)
        if instance.value and isinstance(instance.value, dict):
            data['value'] = {
                'start': instance.value.get('start', ''),
                'end': instance.value.get('end', ''),
                'split': instance.value.get('split', '')
            }
        else:
            data['value'] = {'start': '', 'end': '', 'split': ''}
        return data


class ConfigRequestSerializer(serializers.Serializer):
    """Serializer for ConfigRqm - matches ConfigRqm structure."""
    name = serializers.CharField(required=False, allow_blank=True, default='')
    type = serializers.IntegerField(required=False, default=0)

