"""ASGI config for monsite project.

It exposes the ASGI callable as a module-level variable named ``application``.

This file wires Django + Channels (WebSocket) together.
"""

import os

from django.core.asgi import get_asgi_application
from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "monsite.settings")

django_asgi_app = get_asgi_application()

import chat.routing  # noqa: E402


application = ProtocolTypeRouter(
    {
        "http": django_asgi_app,
        "websocket": AuthMiddlewareStack(URLRouter(chat.routing.websocket_urlpatterns)),
    }
)
