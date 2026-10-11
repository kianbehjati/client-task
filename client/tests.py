from datetime import timedelta

from django.db.utils import IntegrityError
from django.test import TestCase
from django.utils import timezone

from client.models import Client, Otp


class ClientModelTest(TestCase):
    def setUp(self):
        self.client_data = {
            "name": "John",
            "last_name": "Doe",
            "email": "john.doe@example.com",
            "phone_number": "+1234567890",
            "telegram_id": "telegram_123",
        }

    def test_client_creation(self):
        """Test creating a Client instance with all fields."""
        client = Client.objects.create(**self.client_data)
        self.assertEqual(client.name, "John")
        self.assertEqual(client.last_name, "Doe")
        self.assertEqual(client.email, "john.doe@example.com")
        self.assertEqual(client.phone_number, "+1234567890")
        self.assertEqual(client.telegram_id, "telegram_123")
        self.assertIsNotNone(client.created_at)

    def test_client_str_representation(self):
        """Test the __str__ method of Client."""
        client = Client.objects.create(**self.client_data)
        self.assertEqual(str(client), "JohnDoe")

    def test_client_optional_fields(self):
        """Test creating a Client with only required fields (if any, or nullable fields as blank/null)."""
        client = Client.objects.create(name="Jane", last_name="Smith")
        self.assertEqual(client.name, "Jane")
        self.assertEqual(client.last_name, "Smith")
        self.assertIsNone(client.email)
        self.assertIsNone(client.phone_number)
        self.assertIsNone(client.telegram_id)
        self.assertEqual(str(client), "JaneSmith")

    def test_client_unique_email(self):
        """Test that email must be unique if provided."""
        Client.objects.create(**self.client_data)
        duplicate_data = self.client_data.copy()
        duplicate_data["phone_number"] = "+0987654321"
        duplicate_data["telegram_id"] = "telegram_456"

        with self.assertRaises(IntegrityError):
            Client.objects.create(**duplicate_data)

    def test_client_unique_phone_number(self):
        """Test that phone_number must be unique if provided."""
        Client.objects.create(**self.client_data)
        duplicate_data = self.client_data.copy()
        duplicate_data["email"] = "other.email@example.com"
        duplicate_data["telegram_id"] = "telegram_456"

        with self.assertRaises(IntegrityError):
            Client.objects.create(**duplicate_data)

    def test_client_unique_telegram_id(self):
        """Test that telegram_id must be unique if provided."""
        Client.objects.create(**self.client_data)
        duplicate_data = self.client_data.copy()
        duplicate_data["email"] = "other.email@example.com"
        duplicate_data["phone_number"] = "+0987654321"

        with self.assertRaises(IntegrityError):
            Client.objects.create(**duplicate_data)


class OtpModelTest(TestCase):
    def setUp(self):
        self.otp_data = {
            "email": "otp.user@example.com",
            "otp_hash": "dummyhash123",
            "expires_at": timezone.now() + timedelta(minutes=5),
        }

    def test_otp_creation(self):
        """Test creating an Otp instance with default and explicit values."""
        otp = Otp.objects.create(**self.otp_data)
        self.assertEqual(otp.email, "otp.user@example.com")
        self.assertEqual(otp.otp_hash, "dummyhash123")
        self.assertEqual(otp.attempts, 0)
        self.assertFalse(otp.is_used)
        self.assertIsNotNone(otp.created_at)

    def test_otp_str_representation(self):
        """Test the __str__ method of Otp."""
        otp = Otp.objects.create(**self.otp_data)
        self.assertEqual(str(otp), "otp.user@example.com")
