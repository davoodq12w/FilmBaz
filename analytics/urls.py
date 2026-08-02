from django.urls import path
from . import views

app_name = 'analytics'

urlpatterns = [
    path('share/', views.ShareIntractionView.as_view(), name='create_share_intraction'),
    path('watch/interaction/<int:pk>/', views.WatchInteractionView.as_view(), name='watch_interaction'),
]
