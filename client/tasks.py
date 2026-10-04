from celery import shared_task
from django.conf import settings
from django.core.mail import send_mail


@shared_task(
    default_retry_delay=1 * 60,
    retry_kwargs={"max_retries": 2},
    autoretry_for=(ValueError,),
)
def send_otp_email(email: str, otp: str, queue="celery:2") -> str:
    # raise ValueError("error")
    send_mail(
        subject="Your verification code",
        message=f"Your verification code is: {otp}\nThis code expires in 5 minutes.",
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[email],
        fail_silently=True,  # because there is no email backend
    )
    return otp  # NOT SAFE, JUST FOR TEST
