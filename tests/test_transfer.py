from decimal import Decimal

import pytest
from django.urls import reverse
from rest_framework import status

from fantasyfootball.transfer.models import TransferListing


@pytest.mark.django_db
class TestTransferMarket:
    def test_view_transfer_market(self, authenticated_client, transfer_listing):
        url = reverse("transfer-market")
        response = authenticated_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        body = response.json()
        assert body["success"] is True
        assert body["data"]["count"] >= 1

    def test_list_player_for_sale(self, authenticated_client, team):
        player = team.players.first()
        url = reverse("transfer-list-player")
        response = authenticated_client.post(
            url,
            data={"player": str(player.id), "asking_price": "1500000.00"},
            format="json",
        )

        assert response.status_code == status.HTTP_201_CREATED
        assert TransferListing.objects.filter(player=player, is_active=True).exists()

    def test_list_player_not_in_own_team(self, authenticated_client, another_team):
        player = another_team.players.first()
        url = reverse("transfer-list-player")
        response = authenticated_client.post(
            url,
            data={"player": str(player.id), "asking_price": "1500000.00"},
            format="json",
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_list_player_already_listed(self, authenticated_client, player, transfer_listing):
        url = reverse("transfer-list-player")
        response = authenticated_client.post(
            url,
            data={"player": str(player.id), "asking_price": "2000000.00"},
            format="json",
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_remove_listing(self, authenticated_client, transfer_listing):
        url = reverse("transfer-detail", kwargs={"pk": transfer_listing.id})
        response = authenticated_client.delete(url)

        assert response.status_code == status.HTTP_200_OK
        transfer_listing.refresh_from_db()
        assert transfer_listing.is_active is False

    def test_remove_listing_not_owner(self, another_authenticated_client, transfer_listing):
        url = reverse("transfer-detail", kwargs={"pk": transfer_listing.id})
        response = another_authenticated_client.delete(url)

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_filter_by_price_range(self, authenticated_client, transfer_listing):
        url = reverse("transfer-market")
        response = authenticated_client.get(url, {"min_price": "1000000", "max_price": "2000000"})

        assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
class TestBuyPlayer:
    def test_buy_player_success(
        self, another_authenticated_client, another_team, transfer_listing
    ):
        initial_budget = another_team.budget
        price = transfer_listing.asking_price

        url = reverse("transfer-buy", kwargs={"pk": transfer_listing.id})
        response = another_authenticated_client.post(url)

        assert response.status_code == status.HTTP_200_OK
        body = response.json()
        assert body["success"] is True

        transfer_listing.refresh_from_db()
        assert transfer_listing.is_active is False

        another_team.refresh_from_db()
        assert another_team.budget == initial_budget - price

    def test_buy_own_player(self, authenticated_client, transfer_listing):
        url = reverse("transfer-buy", kwargs={"pk": transfer_listing.id})
        response = authenticated_client.post(url)

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_buy_player_insufficient_budget(
        self, another_authenticated_client, another_team, transfer_listing
    ):
        another_team.budget = Decimal("100.00")
        another_team.save()

        url = reverse("transfer-buy", kwargs={"pk": transfer_listing.id})
        response = another_authenticated_client.post(url)

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_player_value_increases_after_transfer(
        self, another_authenticated_client, player, transfer_listing
    ):
        original_value = player.value

        url = reverse("transfer-buy", kwargs={"pk": transfer_listing.id})
        another_authenticated_client.post(url)

        player.refresh_from_db()
        assert player.value > original_value

    def test_buy_player_creates_transaction(
        self, another_authenticated_client, another_user, transfer_listing
    ):
        from fantasyfootball.transaction.models import Transaction

        url = reverse("transfer-buy", kwargs={"pk": transfer_listing.id})
        another_authenticated_client.post(url)

        assert Transaction.objects.filter(buyer=another_user).exists()
