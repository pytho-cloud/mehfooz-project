from django.urls import re_path

# Import consumers at the top level to avoid circular imports
from chatapp import consumer

websocket_urlpatterns = [
    re_path(r'ws/signaling/(?P<room_name>\w+)/$', consumer.SignalingConsumer.as_asgi()),
]
