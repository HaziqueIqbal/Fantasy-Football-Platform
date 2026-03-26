from django.urls import path

from .views import PlayerDetailView, PlayerListView

urlpatterns = [
    path("", PlayerListView.as_view(), name="player-list"),
    path("<uuid:pk>/", PlayerDetailView.as_view(), name="player-detail"),
]
