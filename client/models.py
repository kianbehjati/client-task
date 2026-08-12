from django.db import models


class Client(models.Model):
    name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True, null=True, blank=True)
    phone_number = models.CharField(max_length=15, null=True, blank=True, unique=True) # needs validationd
    created_at = models.DateTimeField(auto_now_add=True)
    telegram_id = models.CharField(max_length=100, blank=True, null=True, unique=True)

    def __str__(self):
        return self.name + self.last_name


class Otp(models.Model):
    email = models.EmailField()
    otp_hash = models.CharField(max_length=128)  # storing hash for security
    expires_at = models.DateTimeField()
    attempts = models.PositiveSmallIntegerField(default=0)
    is_used = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=["email", "created_at"]),
        ]

    def __str__(self):
        return self.email
