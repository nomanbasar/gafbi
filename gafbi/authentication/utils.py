import random
from datetime import timedelta
from django.conf import settings
from django.utils import timezone
from django.core.mail import send_mail


def generate_otp():
    return f"{random.randint(0, 999999):06d}"


def otp_expiry():
    return timezone.now() + timedelta(minutes=settings.OTP_EXPIRE_MINUTES)


def send_otp_email(email, otp, purpose):
    if purpose == "email_verify":
        message = f"Your GAFBI email verification OTP is: {otp}"
    else:
        message = f"Your GAFBI password reset OTP is: {otp}"

    send_mail(
        subject="Your OTP Code",
        message=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[email],
        fail_silently=False,
    )