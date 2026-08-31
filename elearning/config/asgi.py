"""
ASGI config for the eLearning project.

Exposes the ASGI callable, routing HTTP requests through the standard Django
stack and WebSocket connections through Django Channels (R1g).
"""

import os

from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

django_asgi_app = get_asgi_application()

from chat.routing import websocket_urlpatterns  # noqa: E402  (must follow django setup)

application = ProtocolTypeRouter({
    'http': django_asgi_app,
    'websocket': AuthMiddlewareStack(
        URLRouter(websocket_urlpatterns)
    ),
})
