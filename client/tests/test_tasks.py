from django.conf import settings
from pytest_mock import MockerFixture

from client.tasks import send_otp_email


def test_send_otp_email(mocker: MockerFixture):
    mock_send_mail = mocker.patch("client.tasks.send_mail")
    otp = "123456"
    email = "test@test.com"

    res = send_otp_email(otp=otp, email=email)
    assert res == otp
    mock_send_mail.assert_called_once_with(
        subject="Your verification code",
        message=f"Your verification code is: {otp}\nThis code expires in 5 minutes.",
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[email],
        fail_silently=True,
    )
