import pytest

from client.models import Client


@pytest.fixture
def client_create(db) -> Client:
    client_data = {
        "name": "John",
        "last_name": "Doe",
        "email": "john.doe@example.com",
        "phone_number": "+1234567890",
        "telegram_id": "telegram_123",
    }
    client = Client.objects.create(**client_data)
    return client


def test_client_data(client_create: Client) -> None:
    assert client_create.name == "John"
    assert client_create.last_name == "Doe"
    assert client_create.email == "john.doe@example.com"
    assert client_create.phone_number == "+1234567890"
    assert client_create.telegram_id == "telegram_123"


def test_client_str(client_create: Client) -> None:
    assert str(client_create) == "JohnDoe"


@pytest.mark.django_db
def test_optional_fields() -> None:
    client = Client.objects.create(name="John", last_name="Doe")
    assert client.name == "John"
    assert client.last_name == "Doe"
    assert client.email is None
    assert client.telegram_id is None
    assert client.phone_number is None


@pytest.mark.django_db
def test_client_email_uniqueness(client_create: Client) -> None:
    from django.db import IntegrityError

    with pytest.raises(IntegrityError):
        Client.objects.create(
            name="Jane",
            last_name="Doe",
            email=client_create.email,
        )
