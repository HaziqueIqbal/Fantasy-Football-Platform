from django.urls import include, path

urlpatterns = [
    path("v1/transfer/", include("fantasyfootball.transfer.v1.urls")),
]
