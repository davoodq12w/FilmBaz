import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "FilmBaz.settings")

django_asgi_app = get_asgi_application()


def get_support_websocket_routes():
    from support import urls
    return urls.websocket_urlpatterns


application = ProtocolTypeRouter({
    "http": django_asgi_app,
    "websocket": AuthMiddlewareStack(
        URLRouter(
            get_support_websocket_routes()
        )
    )
})
