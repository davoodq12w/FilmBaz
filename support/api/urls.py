from django.urls import path
from . import views

app_name = 'support_api'

urlpatterns = [
    path("support_sessions/admin/", views.AdminSupportSessionsApi.as_view(), name="support_sessions_admin"),
    path("support_sessions/admin/<int:pk>/", views.AdminSupportSessionDetailsApi.as_view(),
         name="support_session_details_admin"),
    path("support_sessions/user/", views.SupportSessionDetailsApi.as_view(), name="support_session_details_user"),
    path("support_sessions/websocker_docs/", views.SupportSocketDocs.as_view(), name="support_sessions_websocker_docs"),
]
