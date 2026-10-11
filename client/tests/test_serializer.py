import pytest

from client.serializer import (
    ClientSerializer,
    RequestOtpSerializer,
    VerifyOtpSerializer,
)


@pytest.mark.django_db
def test_client_serializer_valid_data():
    valid_data = {
        "name": "Alice",
        "last_name": "Smith",
        "email": "alice.smith@example.com",
        "phone_number": "+1987654321",
        "telegram_id": "telegram_alice",
    }
    serializer = ClientSerializer(data=valid_data)
    assert serializer.is_valid(), serializer.errors
    client = serializer.save()
    assert client.name == "Alice"
    assert client.email == "alice.smith@example.com"


@pytest.mark.django_db
def test_client_serializer_missing_required_fields():
    invalid_data = {}
    serializer = ClientSerializer(data=invalid_data)
    assert not serializer.is_valid()
    assert "name" in serializer.errors
    assert "last_name" in serializer.errors


def test_request_otp_serializer():
    valid_data = {"email": "test@example.com"}
    serializer = RequestOtpSerializer(data=valid_data)
    assert serializer.is_valid(), serializer.errors

    invalid_data = {"email": "not-an-email"}
    serializer = RequestOtpSerializer(data=invalid_data)
    assert not serializer.is_valid()
    assert "email" in serializer.errors


def test_verify_otp_serializer():
    valid_data = {"otp": "123456", "email": "test@example.com"}
    serializer = VerifyOtpSerializer(data=valid_data)
    assert serializer.is_valid(), serializer.errors

    invalid_data = {"otp": "123", "email": "test@example.com"}
    serializer = VerifyOtpSerializer(data=invalid_data)
    assert not serializer.is_valid()
    assert "otp" in serializer.errors
