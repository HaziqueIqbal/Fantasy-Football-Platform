from django.urls import include, path

urlpatterns = [
    path("v1/transactions/", include("fantasyfootball.transaction.v1.urls")),
]
