import pytest
from django.urls import reverse
from rest_framework import status


@pytest.mark.django_db
class TestUserRegistration:
    def test_register_success(self, api_client, user_data):
        url = reverse("user-register")
        response = api_client.post(url, data=user_data, format="json")

        assert response.status_code == status.HTTP_201_CREATED
        body = response.json()
        assert body["success"] is True
        assert body["data"]["user"]["email"] == user_data["email"]
        assert "tokens" in body["data"]
        assert "access" in body["data"]["tokens"]

    def test_register_creates_team(self, api_client, user_data):
        url = reverse("user-register")
        api_client.post(url, data=user_data, format="json")

        from django.contrib.auth import get_user_model
        from fantasyfootball.team.models import Team

        User = get_user_model()
        user = User.objects.get(email=user_data["email"])
        assert Team.objects.filter(owner=user).exists()

    def test_register_team_has_20_players(self, api_client, user_data):
        url = reverse("user-register")
        api_client.post(url, data=user_data, format="json")

        from django.contrib.auth import get_user_model

        User = get_user_model()
        user = User.objects.get(email=user_data["email"])
        assert user.team.players.count() == 20

    def test_register_password_mismatch(self, api_client, user_data):
        url = reverse("user-register")
        user_data["password_confirm"] = "WrongPass123!"
        response = api_client.post(url, data=user_data, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_register_duplicate_email(self, api_client, user_data, user):
        url = reverse("user-register")
        user_data["email"] = user.email
        response = api_client.post(url, data=user_data, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_register_missing_fields(self, api_client):
        url = reverse("user-register")
        response = api_client.post(url, data={}, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
class TestUserLogin:
    def test_login_success(self, api_client, user):
        url = reverse("user-login")
        response = api_client.post(
            url,
            data={"email": user.email, "password": "StrongPass123!"},
            format="json",
        )

        assert response.status_code == status.HTTP_200_OK
        body = response.json()
        assert body["success"] is True
        assert "access" in body["data"]["tokens"]

    def test_login_wrong_password(self, api_client, user):
        url = reverse("user-login")
        response = api_client.post(
            url,
            data={"email": user.email, "password": "WrongPass!"},
            format="json",
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_login_nonexistent_email(self, api_client):
        url = reverse("user-login")
        response = api_client.post(
            url,
            data={"email": "nobody@example.com", "password": "SomePass123!"},
            format="json",
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
class TestUserProfile:
    def test_get_profile(self, authenticated_client, user):
        url = reverse("user-profile")
        response = authenticated_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        body = response.json()
        assert body["data"]["email"] == user.email

    def test_update_profile(self, authenticated_client):
        url = reverse("user-profile")
        response = authenticated_client.put(
            url,
            data={"first_name": "Updated"},
            format="json",
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.json()["data"]["first_name"] == "Updated"

    def test_profile_requires_auth(self, api_client):
        url = reverse("user-profile")
        response = api_client.get(url)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
