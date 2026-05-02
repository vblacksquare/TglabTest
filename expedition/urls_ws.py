from django.urls import path
from .consumer import ExpeditionConsumer


websocket_urlpatterns = [
    path("ws/expeditions/", ExpeditionConsumer.as_asgi()),
]
