import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "TglabTest.settings")

from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter

django_asgi_app = get_asgi_application()


def websocket_app():
    from expedition.middleware import JWTAuthMiddleware
    from expedition.urls_ws import websocket_urlpatterns

    return JWTAuthMiddleware(
        URLRouter(websocket_urlpatterns)
    )


application = ProtocolTypeRouter({
    "http": django_asgi_app,
    "websocket": websocket_app(),
})