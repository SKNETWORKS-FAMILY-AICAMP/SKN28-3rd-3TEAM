from rest_framework import serializers
from .models import HealthProfile


class HealthProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = HealthProfile
        fields = [
            "id",
            "age",
            "gender",
            "height",
            "weight",
            "blood_type",
            "pregnancy_status",
            "allergies",
            "diseases",
            "current_medications",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]