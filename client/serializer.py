from rest_framework import serializers
from .models import Client
from django.urls import reverse

class ClientSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='client-detail')
    qr_code = serializers.HyperlinkedIdentityField(view_name='qr_code')

    class Meta:
        model = Client
        fields = '__all__'

class RequestOtpSerializer(serializers.Serializer):
    email = serializers.EmailField()

class VerifyOtpSerializer(serializers.Serializer):
    otp = serializers.CharField(max_length=6,min_length=6)
    email = serializers.EmailField()
    