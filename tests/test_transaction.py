import pytest
from django.urls import reverse
from rest_framework import status

from fantasyfootball.transaction.models import Transaction


@pytest.mark.django_db
class TestTransactionHistory:
    def _create_transaction(self, buyer, seller, player, transfer_listing):
        return Transaction.objects.create(
            player=player,
            from_team=seller.team,
            to_team=buyer.team,
            seller=seller,
            buyer=buyer,
            transfer_amount=1_500_000,
            transfer_listing=transfer_listing,
        )

    def test_list_transactions(
        self, authenticated_client, user, another_user, player, transfer_listing, another_team
    ):
        transaction = self._create_transaction(another_user, user, player, transfer_listing)

        url = reverse("transaction-list")
        response = authenticated_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        body = response.json()
        assert body["success"] is True
        assert body["data"]["count"] >= 1

    def test_transaction_detail(
        self, authenticated_client, user, another_user, player, transfer_listing
    ):
        transaction = self._create_transaction(another_user, user, player, transfer_listing)

        url = reverse("transaction-detail", kwargs={"pk": transaction.id})
        response = authenticated_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.json()["data"]["id"] == str(transaction.id)

    def test_transactions_require_auth(self, api_client):
        url = reverse("transaction-list")
        response = api_client.get(url)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_transaction_cannot_be_deleted(
        self, user, another_user, player, transfer_listing
    ):
        transaction = self._create_transaction(another_user, user, player, transfer_listing)

        with pytest.raises(NotImplementedError):
            transaction.delete()

    def test_filter_transactions_by_buyer(
        self, authenticated_client, user, another_user, player, transfer_listing
    ):
        self._create_transaction(another_user, user, player, transfer_listing)

        url = reverse("transaction-list")
        response = authenticated_client.get(url, {"buyer": str(another_user.id)})

        assert response.status_code == status.HTTP_200_OK
        results = response.json()["data"]["results"]
        for t in results:
            assert t["buyer"] == str(another_user.id)
