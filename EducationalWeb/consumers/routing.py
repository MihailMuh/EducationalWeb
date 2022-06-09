from django.urls import re_path

from .consumers import SessionConsumer

websocket_urlpatterns = [
    re_path("diary", SessionConsumer.as_asgi()),
]
