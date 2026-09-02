"""
ASGI config for the EDUMON project.

Exposes the ASGI callable, routing HTTP requests through the standard Django
stack and WebSocket connections through Django Channels (R1g).
"""

import os

from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

django_asgi_app = get_asgi_application()

from chat.routing import websocket_urlpatterns as chat_websocket_urlpatterns  # noqa: E402
from notifications.routing import websocket_urlpatterns as notification_websocket_urlpatterns  # noqa: E402

application = ProtocolTypeRouter({
    'http': django_asgi_app,
    'websocket': AuthMiddlewareStack(
        URLRouter(chat_websocket_urlpatterns + notification_websocket_urlpatterns)
    ),
})
