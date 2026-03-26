from django.urls import path

from .views import (
    BuyPlayerView,
    ListPlayerForSaleView,
    TransferListingDetailView,
    TransferMarketView,
)

urlpatterns = [
    path("", TransferMarketView.as_view(), name="transfer-market"),
    path("list/", ListPlayerForSaleView.as_view(), name="transfer-list-player"),
    path("<uuid:pk>/", TransferListingDetailView.as_view(), name="transfer-detail"),
    path("<uuid:pk>/buy/", BuyPlayerView.as_view(), name="transfer-buy"),
]
