import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

from fantasyfootball.player.models import Player
from fantasyfootball.team.models import Team
from fantasyfootball.transfer.models import TransferListing

User = get_user_model()


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def user_data():
    return {
        "email": "testuser@example.com",
        "first_name": "Test",
        "last_name": "User",
        "password": "TestPass123!",
        "password_confirm": "TestPass123!",
    }


@pytest.fixture
def user(db):
    u = User.objects.create_user(
        email="user@example.com",
        first_name="John",
        last_name="Doe",
        password="StrongPass123!",
    )
    return u


@pytest.fixture
def another_user(db):
    u = User.objects.create_user(
        email="another@example.com",
        first_name="Jane",
        last_name="Smith",
        password="StrongPass123!",
    )
    return u


@pytest.fixture
def authenticated_client(api_client, user):
    api_client.force_authenticate(user=user)
    return api_client


@pytest.fixture
def another_authenticated_client(api_client, another_user):
    client = APIClient()
    client.force_authenticate(user=another_user)
    return client


@pytest.fixture
def team(user):
    try:
        return user.team
    except Exception:
        from fantasyfootball.team.services import TeamService
        return TeamService.create_team_for_user(user)


@pytest.fixture
def another_team(another_user):
    try:
        return another_user.team
    except Exception:
        from fantasyfootball.team.services import TeamService
        return TeamService.create_team_for_user(another_user)


@pytest.fixture
def player(team):
    return team.players.first()


@pytest.fixture
def transfer_listing(player, user):
    return TransferListing.objects.create(
        player=player,
        seller=user,
        asking_price=1_500_000,
        is_active=True,
    )
