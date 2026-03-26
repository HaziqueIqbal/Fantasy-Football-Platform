from django.urls import include, path

urlpatterns = [
    path("v1/players/", include("fantasyfootball.player.v1.urls")),
]
