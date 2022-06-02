from django.urls import re_path

from .consumers import SessionConsumer

session = SessionConsumer.as_asgi()

websocket_urlpatterns = [
    re_path("diary", session),
]
