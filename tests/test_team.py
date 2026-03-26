import pytest
from django.urls import reverse
from rest_framework import status

from fantasyfootball.player.models import Player


@pytest.mark.django_db
class TestTeamCreation:
    def test_team_created_on_registration(self, user):
        """Signal creates team automatically on user creation."""
        assert hasattr(user, "team")

    def test_team_initial_budget(self, team):
        assert team.budget == 5_000_000

    def test_team_has_20_players(self, team):
        assert team.players.count() == 20

    def test_team_player_distribution(self, team):
        players = team.players.all()
        positions = {p.position for p in players}
        assert positions == {"goalkeeper", "defender", "midfielder", "attacker"}
        assert players.filter(position="goalkeeper").count() == 3
        assert players.filter(position="defender").count() == 5
        assert players.filter(position="midfielder").count() == 6
        assert players.filter(position="attacker").count() == 6

    def test_player_initial_value(self, team):
        for player in team.players.all():
            assert player.value == 1_000_000

    def test_team_total_value(self, team):
        assert team.total_value == 20_000_000


@pytest.mark.django_db
class TestTeamAPI:
    def test_get_my_team(self, authenticated_client, team):
        url = reverse("my-team")
        response = authenticated_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        body = response.json()
        assert body["success"] is True
        assert body["data"]["id"] == str(team.id)

    def test_get_my_team_unauthenticated(self, api_client):
        url = reverse("my-team")
        response = api_client.get(url)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_list_teams(self, authenticated_client, team):
        url = reverse("team-list")
        response = authenticated_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.json()["success"] is True

    def test_team_detail(self, authenticated_client, team):
        url = reverse("team-detail", kwargs={"pk": team.id})
        response = authenticated_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.json()["data"]["id"] == str(team.id)

    def test_team_detail_not_found(self, authenticated_client):
        import uuid
        url = reverse("team-detail", kwargs={"pk": uuid.uuid4()})
        response = authenticated_client.get(url)

        assert response.status_code == status.HTTP_404_NOT_FOUND
