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


def set_refresh_cookie(response, refresh_token):
    response.set_cookie(
        key=settings.AUTH_REFRESH_COOKIE_NAME,
        value=refresh_token,
        max_age=int(
            settings.SIMPLE_JWT[
                "REFRESH_TOKEN_LIFETIME"
            ].total_seconds()
        ),
        httponly=True,
        secure=settings.AUTH_COOKIE_SECURE,
        samesite=settings.AUTH_COOKIE_SAMESITE,
        path=settings.AUTH_COOKIE_PATH,
        domain=settings.AUTH_COOKIE_DOMAIN,
    )
    return response


def delete_refresh_cookie(response):
    response.delete_cookie(
        key=settings.AUTH_REFRESH_COOKIE_NAME,
        path=settings.AUTH_COOKIE_PATH,
        domain=settings.AUTH_COOKIE_DOMAIN,
        samesite=settings.AUTH_COOKIE_SAMESITE,
    )
    return response


def move_refresh_token_to_cookie(response, data):
    tokens = (
        data.get("tokens")
        if isinstance(data, dict)
        else None
    )

    if isinstance(tokens, dict):
        refresh_token = tokens.pop(
            "refresh",
            None
        )

        if refresh_token:
            set_refresh_cookie(
                response,
                refresh_token
            )

    return response