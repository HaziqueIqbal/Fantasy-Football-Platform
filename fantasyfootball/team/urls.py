from django.urls import include, path

urlpatterns = [
    path("v1/teams/", include("fantasyfootball.team.v1.urls")),
]
