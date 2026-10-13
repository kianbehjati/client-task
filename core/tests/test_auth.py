import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from client.models import Client


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def user(db):
    User = get_user_model()
    user = User.objects.create(username="test")
    user.set_password("test")
    user.save()
    return user


@pytest.fixture
def admin_user(db):
    User = get_user_model()
    return User.objects.create_superuser(
        username="admin", email="admin@example.com", password="password"
    )


@pytest.fixture
def access_token(user):
    return str(RefreshToken.for_user(user).access_token)


@pytest.fixture
def admin_access_token(admin_user):
    return str(RefreshToken.for_user(admin_user).access_token)


@pytest.fixture
def refresh_token(user):
    return str(RefreshToken.for_user(user))


def test_token_endpoint(user, api_client: APIClient):
    url = reverse("token_obtain_pair")
    res = api_client.post(
        path=url, data={"username": "test", "password": "test"}, format="json"
    )
    assert res.status_code == 200

    data = res.data
    assert data["refresh"]
    assert data["access"]


def test_token_endpoint_wrong_cred(db, api_client: APIClient):
    url = reverse("token_obtain_pair")
    res = api_client.post(
        path=url, data={"username": "test", "password": "test"}, format="json"
    )
    assert res.status_code != 200
    assert "No active account" in res.data["detail"]


def test_token_refresh_endpoint(refresh_token, api_client: APIClient):
    url = reverse("token_refresh")
    res = api_client.post(path=url, data={"refresh": refresh_token}, format="json")
    assert res.status_code == 200
    assert "access" in res.data


def test_token_refresh_endpoint_invalid(api_client: APIClient):
    url = reverse("token_refresh")
    res = api_client.post(path=url, data={"refresh": "invalid_token"}, format="json")
    assert res.status_code == 401


@pytest.mark.django_db
def test_client_create_with_jwt_admin_permission(
    admin_access_token, access_token, api_client: APIClient
):
    url = reverse("client-list")
    client_data = {
        "name": "JWTAuth",
        "last_name": "Test",
        "email": "jwtauth.client@example.com",
        "phone_number": "+19998887766",
        "telegram_id": "jwtauth_telegram",
    }

    # 1. Try with regular user token (should fail IsAdminUser with 403)
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {access_token}")
    res_regular = api_client.post(url, client_data, format="json")
    assert res_regular.status_code == 403

    # 2. Try with admin user token (should succeed with 201)
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {admin_access_token}")
    res_admin = api_client.post(url, client_data, format="json")
    assert res_admin.status_code == 201
    assert Client.objects.filter(email="jwtauth.client@example.com").exists()
