from django.urls import path
from .views import chat, chat_history

urlpatterns = [
    path('', chat),
    path('history/', chat_history),
]