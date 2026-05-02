from datetime import timedelta
from django.conf import settings
from django.utils import timezone
from rest_framework import serializers
from rest_framework_simplejwt.token_blacklist.models import OutstandingToken, BlacklistedToken

from .models import OTP


def enforce_resend_limits(user, email, purpose):
    last_otp = OTP.objects.filter(
        user=user,
        email_address=email,
        purpose=purpose
    ).order_by("-created_at").first()

    if last_otp and (timezone.now() - last_otp.created_at) < timedelta(seconds=settings.OTP_RESEND_COOLDOWN_SECONDS):
        raise serializers.ValidationError("please_wait_before_resend")

    one_hour_ago = timezone.now() - timedelta(hours=1)

    count_last_hour = OTP.objects.filter(
        user=user,
        email_address=email,
        purpose=purpose,
        created_at__gte=one_hour_ago
    ).count()

    if count_last_hour >= settings.OTP_RESEND_MAX_PER_HOUR:
        raise serializers.ValidationError("resend_limit_exceeded")


def enforce_otp_attempt_limit(otp_obj):
    if otp_obj.attempt_count >= settings.OTP_MAX_ATTEMPTS:
        raise serializers.ValidationError("too_many_attempts_try_later")


def blacklist_all_refresh_tokens(user):
    for token in OutstandingToken.objects.filter(user=user):
        BlacklistedToken.objects.get_or_create(token=token)