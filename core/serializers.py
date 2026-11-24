from rest_framework import serializers
from .models import Request

class RequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = Request
        fields = '__all__'
        read_only_fields = ['resident', 'executor', 'status', 'created_at']

    def validate_description(self, value):
        if len(value) < 10:
            raise serializers.ValidationError("Описание должно быть не менее 10 символов.")
        return value