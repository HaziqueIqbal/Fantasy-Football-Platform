from django.urls import include, path

urlpatterns = [
    path("user/", include("fantasyfootball.user.urls")),
    path("team/", include("fantasyfootball.team.urls")),
    path("player/", include("fantasyfootball.player.urls")),
    path("transfer/", include("fantasyfootball.transfer.urls")),
    path("transaction/", include("fantasyfootball.transaction.urls")),
]
