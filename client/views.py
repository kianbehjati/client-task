from .serializer import ClientSerializer, RequestOtpSerializer, VerifyOtpSerializer
from .models import Client, Otp

from rest_framework.permissions import IsAdminUser
from rest_framework.reverse import reverse
from rest_framework.viewsets import ModelViewSet, GenericViewSet
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser
from rest_framework.views import APIView

from django.http.response import (
    HttpResponseForbidden,
    HttpResponse,
    HttpResponseNotFound,
)

from django.core.mail import send_mail
from django.conf import settings
from django.db.models import F
from django.utils import timezone
from django.contrib.auth import get_user_model, login
from django_filters.rest_framework import DjangoFilterBackend

from django_q.tasks import async_task
import qrcode
import io
import hashlib
import secrets
from datetime import timedelta
import csv
from kavenegar import *

### internal functions ###
def generate_otp() -> str:
    return f"{secrets.randbelow(1000000):06d}"


def hash_otp(otp: str) -> str:
    return hashlib.sha256(f"{settings.SECRET_KEY}:{otp}".encode()).hexdigest()


def send_otp_email(email: str, otp: str) -> None:
    send_mail(
        subject="Your verification code",
        message=f"Your verification code is: {otp}\nThis code expires in 5 minutes.",
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[email],
        fail_silently=True,  # because there is no email backend
    )


def qr_code(request, pk):
    # isAdmin permission
    if not request.user or not request.user.is_staff:
        return HttpResponseForbidden()

    else:
        client = Client.objects.filter(id=pk).only("id")
        if not client.exists():
            return HttpResponseNotFound("No user was found with this unique ID")
        else:
            url = reverse("client-detail", kwargs={"pk": pk}, request=request)

    qr = qrcode.make(url)

    buffer = io.BytesIO()
    qr.save(buffer, format="PNG")

    return HttpResponse(
        buffer.getvalue(),
        content_type="image/png",
    )


### API VIEWS ###
class ClientViewSet(ModelViewSet):
    """
    /api/Client/<PK> -> Update/Delete Client\n
    /api/Client -> List Clients
    """

    serializer_class = ClientSerializer
    queryset = Client.objects.all()
    permission_classes = [IsAdminUser]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = [
        "name",
        "last_name",
        "created_at",
    ]  # custom filter set for iexact and contains searchs
    # pagination can be useful


class AuthenticationViewSet(GenericViewSet):
    serializer_class = RequestOtpSerializer  # just to bypass error needs to be replaced by DefaultSerializer

    def get_serializer_class(self):
        if self.action == "request_otp":
            return RequestOtpSerializer

        if self.action == "verify_otp":
            return VerifyOtpSerializer

        return super().get_serializer_class()

    @action(
        methods=["post"], detail=False, url_name="request otp", url_path="request-otp"
    )
    def request_otp(self, request):
        serialzer = RequestOtpSerializer(data=request.data)
        serialzer.is_valid(raise_exception=True)
        email = serialzer.validated_data["email"]
        Otp.objects.filter(email__iexact=email, is_used=False).update(
            is_used=~F("is_used")
        )  # invalidate previous OTPs
        otp = generate_otp()

        Otp.objects.create(
            email=email,
            otp_hash=hash_otp(otp),
            expires_at=timezone.now() + timedelta(minutes=5),
        )
        print(otp)
        async_task(send_otp_email, email, otp)

        ### kavenegar ###
        '''
        api = KavenegarAPI('API Key')
        params = {
            'receptor': '09xxxxxxxxx',#multiple mobile number, split by comma
            'message': f"Your verification code is: {otp}\nThis code expires in 5 minutes.",
        } 
        async_task(api.sms_send, params)
            or
        api.sms_send(params)
        '''

        return Response(status=status.HTTP_201_CREATED)

    @action(
        methods=["post"], detail=False, url_name="verify otp", url_path="verify-otp"
    )
    def verify_otp(self, request):
        serilizer = VerifyOtpSerializer(data=request.data)
        serilizer.is_valid(raise_exception=True)
        email = serilizer.validated_data["email"]
        otp = serilizer.validated_data["otp"]

        record = (
            Otp.objects.filter(email=email, is_used=False)
            .order_by("-created_at")
            .first()
        )

        if not record:
            return Response(
                {"detail": "Invalid or expired OTP."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if timezone.now() >= record.expires_at:
            record.is_used = True
            record.save()

            return Response(
                {"detail": "Invalid or expired OTP."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if record.attempts >= 3:
            record.is_used = True
            record.save()

            return Response(
                {"detail": "Too many attempts."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        record.attempts += 1
        record.save()

        if not secrets.compare_digest(record.otp_hash, hash_otp(otp)):
            return Response(
                {"detail": "Invalid or expired OTP."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        record.is_used = True
        record.save()

        User = get_user_model()

        user = User.objects.filter(
            email=email,
        )
        if not user:
            return Response(
                {"detail": "Please First create a User with email"},
                status=status.HTTP_406_NOT_ACCEPTABLE,
            )

        login(request, user.first())

        return Response(
            {"detail": "Login successful."},
            status=status.HTTP_200_OK,
        )


class CSVUploadView(
    APIView
):  # APIView because there is no serializer for this view and we are not using any model
    parser_classes = [MultiPartParser]

    def post(self, request):
        csv_file = request.FILES.get("file")
        if not csv_file:
            return Response(
                {"error": "No file provided."}, status=status.HTTP_400_BAD_REQUEST
            )
        text_file = io.TextIOWrapper(csv_file.file, encoding="utf-8-sig")
        reader = csv.DictReader(text_file)
        if set(reader.fieldnames) != set(
            ["name", "last_name", "email", "phone_number", "telegram_id"]
        ):  # has a bug if the csv file has extra columns(with same names)
            return Response(
                {"error": "Invalid CSV format."}, status=status.HTTP_400_BAD_REQUEST
            )

        # can use bulK_create but it will not call the save method of the model so we are using create method in a loop
        for row in reader:
            Client.objects.get_or_create(
                name=row["name"],
                last_name=row["last_name"],
                email=row["email"],
                phone_number=row["phone_number"],
                telegram_id=row["telegram_id"],
            )
        return Response(status=status.HTTP_201_CREATED)
