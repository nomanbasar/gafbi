from django.contrib.auth import authenticate
from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken

from .models import User, OTP
from .utils import generate_otp, otp_expiry, send_otp_email
from .security import enforce_resend_limits, enforce_otp_attempt_limit, blacklist_all_refresh_tokens


# def user_response(user):
#     return {
#         "id": str(user.id),
#         "email_address": user.email_address,
#         "is_email_verified": user.is_email_verified,
#     }
def user_response(user):
    latest_application = user.carebox_applications.order_by("-created_at").first()

    if latest_application:
        name = f"{latest_application.first_name} {latest_application.last_name}"
    else:
        name = user.email_address.split("@")[0]

    image = None

    if hasattr(user, "image") and user.image:
        image = user.image.url
    elif hasattr(user, "profile_image") and user.profile_image:
        image = user.profile_image.url
    elif hasattr(user, "avatar") and user.avatar:
        image = user.avatar.url

    role = "admin" if user.is_staff or user.is_superuser else "user"

    return {
        "id": str(user.id),
        "name": name,
        "image": image,
        "email_address": user.email_address,
        "role": role,
        "is_email_verified": user.is_email_verified,
    }


def token_response(user):
    refresh = RefreshToken.for_user(user)
    return {
        "access": str(refresh.access_token),
        "refresh": str(refresh),
    }


class SignupSerializer(serializers.Serializer):
    email_address = serializers.EmailField()
    password = serializers.CharField(min_length=6, write_only=True)
    confirm_password = serializers.CharField(min_length=6, write_only=True)

    def validate_email_address(self, value):
        if User.objects.filter(email_address=value).exists():
            raise serializers.ValidationError("email_already_exists")
        return value

    def validate(self, attrs):
        if attrs["password"] != attrs["confirm_password"]:
            raise serializers.ValidationError("password_not_match")
        return attrs

    def create(self, validated_data):
        user = User.objects.create_user(
            email_address=validated_data["email_address"],
            password=validated_data["password"],
        )

        user.is_active = False
        user.is_email_verified = False
        user.save(update_fields=["is_active", "is_email_verified"])

        otp_code = generate_otp()

        otp_obj = OTP.objects.create(
            user=user,
            email_address=user.email_address,
            purpose="email_verify",
            otp_code=otp_code,
            expires_at=otp_expiry(),
        )

        send_otp_email(user.email_address, otp_code, "email_verify")

        return {
            "email_address": user.email_address,
            "otp_expires_at": otp_obj.expires_at,
        }


class VerifyEmailSerializer(serializers.Serializer):
    email_address = serializers.EmailField()
    otp_code = serializers.CharField(min_length=6, max_length=6)

    def create(self, validated_data):
        email = validated_data["email_address"]
        otp_code = validated_data["otp_code"]

        user = User.objects.filter(email_address=email).first()
        if not user:
            raise serializers.ValidationError("user_not_found")

        if user.is_email_verified:
            raise serializers.ValidationError("email_already_verified")

        otp_obj = OTP.objects.filter(
            user=user,
            email_address=email,
            purpose="email_verify",
            is_verified=False,
        ).order_by("-created_at").first()

        if not otp_obj:
            raise serializers.ValidationError("otp_not_found")

        if otp_obj.is_expired():
            raise serializers.ValidationError("otp_expired")

        enforce_otp_attempt_limit(otp_obj)

        otp_obj.attempt_count += 1
        otp_obj.save(update_fields=["attempt_count"])

        if otp_obj.otp_code != otp_code:
            raise serializers.ValidationError("invalid_otp")

        otp_obj.is_verified = True
        otp_obj.save(update_fields=["is_verified"])

        user.is_email_verified = True
        user.is_active = True
        user.save(update_fields=["is_email_verified", "is_active"])

        return {
            "user": user_response(user),
            "tokens": token_response(user),
        }


class LoginSerializer(serializers.Serializer):
    email_address = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def create(self, validated_data):
        email = validated_data["email_address"]
        password = validated_data["password"]

        user = User.objects.filter(email_address=email).first()

        if not user:
            raise serializers.ValidationError("invalid_credentials")

        if not user.is_email_verified or not user.is_active:
            raise serializers.ValidationError("email_not_verified")

        user = authenticate(email_address=email, password=password)

        if user is None:
            raise serializers.ValidationError("invalid_credentials")

        return {
            "user": user_response(user),
            "tokens": token_response(user),
        }


class ResendEmailVerifyOtpSerializer(serializers.Serializer):
    email_address = serializers.EmailField()

    def create(self, validated_data):
        email = validated_data["email_address"]

        user = User.objects.filter(email_address=email).first()
        if not user:
            raise serializers.ValidationError("user_not_found")

        if user.is_email_verified:
            raise serializers.ValidationError("email_already_verified")

        enforce_resend_limits(user, email, "email_verify")

        otp_code = generate_otp()

        otp_obj = OTP.objects.create(
            user=user,
            email_address=email,
            purpose="email_verify",
            otp_code=otp_code,
            expires_at=otp_expiry(),
        )

        send_otp_email(email, otp_code, "email_verify")

        return {
            "email_address": email,
            "otp_expires_at": otp_obj.expires_at,
        }


class ForgotPasswordSerializer(serializers.Serializer):
    email_address = serializers.EmailField()

    def create(self, validated_data):
        email = validated_data["email_address"]

        user = User.objects.filter(email_address=email).first()
        if not user:
            raise serializers.ValidationError("user_not_found")

        otp_code = generate_otp()

        otp_obj = OTP.objects.create(
            user=user,
            email_address=email,
            purpose="password_reset",
            otp_code=otp_code,
            expires_at=otp_expiry(),
        )

        send_otp_email(email, otp_code, "password_reset")

        return {
            "email_address": email,
            "otp_expires_at": otp_obj.expires_at,
        }


class ResendForgotPasswordOtpSerializer(serializers.Serializer):
    email_address = serializers.EmailField()

    def create(self, validated_data):
        email = validated_data["email_address"]

        user = User.objects.filter(email_address=email).first()
        if not user:
            raise serializers.ValidationError("user_not_found")

        enforce_resend_limits(user, email, "password_reset")

        otp_code = generate_otp()

        otp_obj = OTP.objects.create(
            user=user,
            email_address=email,
            purpose="password_reset",
            otp_code=otp_code,
            expires_at=otp_expiry(),
        )

        send_otp_email(email, otp_code, "password_reset")

        return {
            "email_address": email,
            "otp_expires_at": otp_obj.expires_at,
        }


class VerifyForgotPasswordOtpSerializer(serializers.Serializer):
    email_address = serializers.EmailField()
    otp_code = serializers.CharField(min_length=6, max_length=6)

    def create(self, validated_data):
        email = validated_data["email_address"]
        otp_code = validated_data["otp_code"]

        user = User.objects.filter(email_address=email).first()
        if not user:
            raise serializers.ValidationError("user_not_found")

        otp_obj = OTP.objects.filter(
            user=user,
            email_address=email,
            purpose="password_reset",
            is_verified=False,
        ).order_by("-created_at").first()

        if not otp_obj:
            raise serializers.ValidationError("otp_not_found")

        if otp_obj.is_expired():
            raise serializers.ValidationError("otp_expired")

        enforce_otp_attempt_limit(otp_obj)

        otp_obj.attempt_count += 1
        otp_obj.save(update_fields=["attempt_count"])

        if otp_obj.otp_code != otp_code:
            raise serializers.ValidationError("invalid_otp")

        otp_obj.is_verified = True
        otp_obj.save(update_fields=["is_verified"])

        
        refresh = RefreshToken.for_user(user)

        return {
            "user": {
                "id": str(user.id),
                "email_address": user.email_address,
                "is_email_verified": user.is_email_verified,
            },
            "tokens": {
                "access": str(refresh.access_token),
                "refresh": str(refresh),
            }
        }


class ResetPasswordSerializer(serializers.Serializer):
    new_password = serializers.CharField(min_length=6, write_only=True)
    confirm_password = serializers.CharField(min_length=6, write_only=True)

    def validate(self, attrs):
        if attrs["new_password"] != attrs["confirm_password"]:
            raise serializers.ValidationError("password_not_match")
        return attrs

    def create(self, validated_data):
        request = self.context["request"]
        user = request.user

        if not user or not user.is_authenticated:
            raise serializers.ValidationError("authentication_required")

        user.set_password(validated_data["new_password"])
        user.save(update_fields=["password"])

        blacklist_all_refresh_tokens(user)

        refresh = RefreshToken.for_user(user)

        return {
            "user": {
                "email_address": user.email_address,
            },
            "tokens": {
                "access": str(refresh.access_token),
                "refresh": str(refresh),
            }
        }



class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(min_length=6, write_only=True)
    confirm_password = serializers.CharField(min_length=6, write_only=True)

    def validate(self, attrs):
        if attrs["new_password"] != attrs["confirm_password"]:
            raise serializers.ValidationError("password_not_match")
        return attrs

    def create(self, validated_data):
        user = self.context["request"].user

        if not user.check_password(validated_data["old_password"]):
            raise serializers.ValidationError("old_password_not_match")

        user.set_password(validated_data["new_password"])
        user.save(update_fields=["password"])

        blacklist_all_refresh_tokens(user)

        return {
            "user": user_response(user),
            "tokens": token_response(user),
        }