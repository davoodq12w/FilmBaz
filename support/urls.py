from django.urls import path, re_path
from . import views
from . import consumers

app_name = "support"

urlpatterns = [
    path("support_session/", views.SupportSessionView.as_view(), name="get_support_session"),
]

websocket_urlpatterns = [
    re_path(r"^ws/support_chat/(?P<support_session_id>\d+)/$", consumers.SupportChatConsumer.as_asgi()),
]
