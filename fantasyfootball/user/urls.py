from django.urls import include, path

urlpatterns = [
    path("v1/", include("fantasyfootball.user.v1.urls")),
]
