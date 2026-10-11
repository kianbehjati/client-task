import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APIClient

from client.models import Client


@pytest.fixture
def admin_user(db):
    User = get_user_model()
    return User.objects.create_superuser(
        username="admin", email="admin@example.com", password="password"
    )


@pytest.fixture
def regular_user(db):
    User = get_user_model()
    return User.objects.create_user(
        username="user", email="user@example.com", password="password"
    )


@pytest.fixture
def api_client():
    return APIClient()


@pytest.mark.django_db
def test_client_viewset_list_unauthorized(api_client):
    url = reverse("client-list")
    response = api_client.get(url)
    assert response.status_code in (401, 403)


@pytest.mark.django_db
def test_client_viewset_list_as_regular_user(api_client, regular_user):
    api_client.force_authenticate(user=regular_user)
    url = reverse("client-list")
    response = api_client.get(url)
    assert response.status_code == 403


@pytest.mark.django_db
def test_client_viewset_list_as_admin(api_client, admin_user):
    api_client.force_authenticate(user=admin_user)
    url = reverse("client-list")
    response = api_client.get(url)
    assert response.status_code == 200


@pytest.mark.django_db
def test_client_viewset_create_as_admin(api_client, admin_user):
    api_client.force_authenticate(user=admin_user)
    url = reverse("client-list")
    data = {
        "name": "Test",
        "last_name": "Client",
        "email": "test.client@example.com",
        "phone_number": "+1234567890",
        "telegram_id": "test_telegram",
    }
    response = api_client.post(url, data)
    assert response.status_code == 201
    assert Client.objects.filter(email="test.client@example.com").exists()
