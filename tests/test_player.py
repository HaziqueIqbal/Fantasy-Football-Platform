import pytest
from django.urls import reverse
from rest_framework import status


@pytest.mark.django_db
class TestPlayerAPI:
    def test_list_players(self, authenticated_client, team):
        url = reverse("player-list")
        response = authenticated_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        body = response.json()
        assert body["success"] is True
        assert body["data"]["count"] >= 20

    def test_player_detail(self, authenticated_client, player):
        url = reverse("player-detail", kwargs={"pk": player.id})
        response = authenticated_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.json()["data"]["id"] == str(player.id)

    def test_player_detail_not_found(self, authenticated_client):
        import uuid
        url = reverse("player-detail", kwargs={"pk": uuid.uuid4()})
        response = authenticated_client.get(url)

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_filter_players_by_position(self, authenticated_client, team):
        url = reverse("player-list")
        response = authenticated_client.get(url, {"position": "goalkeeper"})

        assert response.status_code == status.HTTP_200_OK
        results = response.json()["data"]["results"]
        for p in results:
            assert p["position"] == "goalkeeper"

    def test_search_players(self, authenticated_client, team):
        player = team.players.first()
        url = reverse("player-list")
        response = authenticated_client.get(url, {"search": player.last_name})

        assert response.status_code == status.HTTP_200_OK

    def test_list_players_requires_auth(self, api_client):
        url = reverse("player-list")
        response = api_client.get(url)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
