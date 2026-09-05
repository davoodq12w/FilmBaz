from django.contrib import admin
from django.urls import path, include
from django.conf.urls import handler404
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('film.urls', namespace="film")),
    path('account/', include('account.urls', namespace="account")),
    path('support/', include('support.urls', namespace="support")),
    path('people/', include('people.urls', namespace="people")),
    path('analytics/', include('analytics.urls', namespace="analytics")),
    path("api-auth/", include('rest_framework.urls')),
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/swagger/", SpectacularSwaggerView.as_view(), name="swagger"),
    path("api/redoc/", SpectacularRedocView.as_view(), name="redoc"),

]

handler404 = "film.views.page_not_found"
