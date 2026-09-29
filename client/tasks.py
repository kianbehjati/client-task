from celery import shared_task
from django.conf import settings
from django.core.mail import send_mail


@shared_task
def send_otp_email(email: str, otp: str) -> str:
    send_mail(
        subject="Your verification code",
        message=f"Your verification code is: {otp}\nThis code expires in 5 minutes.",
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[email],
        fail_silently=True,  # because there is no email backend
    )
    return otp  # NOT SAFE, JUST FOR TEST
