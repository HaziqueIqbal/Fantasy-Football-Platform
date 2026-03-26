from django.urls import path

from .views import MyTeamView, TeamDetailView, TeamListView

urlpatterns = [
    path("", TeamListView.as_view(), name="team-list"),
    path("my/", MyTeamView.as_view(), name="my-team"),
    path("<uuid:pk>/", TeamDetailView.as_view(), name="team-detail"),
]
