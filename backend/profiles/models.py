from django.db import models
from django.contrib.auth.models import User


class HealthProfile(models.Model):
    GENDER_CHOICES = [
        ("MALE", "남성"),
        ("FEMALE", "여성"),
        ("OTHER", "기타"),
    ]

    BLOOD_TYPE_CHOICES = [
        ("UNKNOWN", "미입력"),
        ("A+", "A+"),
        ("A-", "A-"),
        ("B+", "B+"),
        ("B-", "B-"),
        ("AB+", "AB+"),
        ("AB-", "AB-"),
        ("O+", "O+"),
        ("O-", "O-"),
    ]

    PREGNANCY_CHOICES = [
        ("NONE", "해당 없음"),
        ("PREGNANT", "임신 중"),
        ("BREASTFEEDING", "수유 중"),
    ]

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="health_profile"
    )

    age = models.IntegerField()
    gender = models.CharField(max_length=20, choices=GENDER_CHOICES)
    height = models.FloatField(null=True, blank=True)
    weight = models.FloatField(null=True, blank=True)

    blood_type = models.CharField(
        max_length=10,
        choices=BLOOD_TYPE_CHOICES,
        default="UNKNOWN"
    )

    pregnancy_status = models.CharField(
        max_length=20,
        choices=PREGNANCY_CHOICES,
        default="NONE"
    )

    allergies = models.TextField(default="없음", blank=True)
    diseases = models.TextField(default="없음", blank=True)
    current_medications = models.TextField(default="없음", blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} 건강정보"