from django.contrib import admin
from django.urls import path, include
from django.conf.urls import handler404
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('film.urls', namespace="film")),
    path('api/film/', include('film.api.urls', namespace="film_api")),
    path('account/', include('account.urls', namespace="account")),
    path("api/account/", include("account.api.urls", namespace="account_api")),
    path('support/', include('support.urls', namespace="support")),
    path('people/', include('people.urls', namespace="people")),
    path('analytics/', include('analytics.urls', namespace="analytics")),
    path('api/analytics/', include('analytics.api.urls', namespace="analytics_api")),
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/docs/", SpectacularSwaggerView.as_view(), name="swagger"),
    path("api/redoc/", SpectacularRedocView.as_view(), name="redoc"),

]

handler404 = "film.views.page_not_found"
