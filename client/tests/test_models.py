from datetime import timedelta

import pytest
from django.utils import timezone

from client.models import Client, Otp


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


@pytest.fixture
def otp_create(db) -> Otp:
    return Otp.objects.create(
        email="test@example.com",
        otp_hash="somehash123",
        expires_at=timezone.now() + timedelta(minutes=5),
        attempts=0,
        is_used=False,
    )


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


def test_otp_data(otp_create: Otp) -> None:
    assert otp_create.email == "test@example.com"
    assert otp_create.otp_hash == "somehash123"
    assert otp_create.attempts == 0
    assert otp_create.is_used is False
    assert otp_create.created_at is not None
    assert otp_create.expires_at is not None


def test_otp_str(otp_create: Otp) -> None:
    assert str(otp_create) == "test@example.com"


@pytest.mark.django_db
def test_otp_defaults() -> None:
    expires = timezone.now() + timedelta(minutes=10)
    otp = Otp.objects.create(
        email="defaults@example.com",
        otp_hash="hashval",
        expires_at=expires,
    )
    assert otp.attempts == 0
    assert otp.is_used is False
    assert otp.created_at is not None
