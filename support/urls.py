from django.urls import path, re_path
from . import views
from . import consumers

app_name = "support"

urlpatterns = [
    path("support_session/", views.SupportSessionView.as_view(), name="get_support_session"),
    path("support_session_4_admin/<int:support_session_id>/", views.get_support_session_for_admin,
         name="get_support_session_for_admin"),
]

websocket_urlpatterns = [
    re_path(r"^ws/support_chat/(?P<support_session_id>\d+)/$", consumers.SupportChatConsumer.as_asgi()),
]
