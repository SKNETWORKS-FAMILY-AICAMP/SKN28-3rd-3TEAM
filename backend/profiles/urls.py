from django.urls import path
from .views import health_profile

urlpatterns = [
    path('', health_profile),
]