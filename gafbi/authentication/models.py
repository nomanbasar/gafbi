import uuid
from django.db import models
from django.utils import timezone
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager


class UserManager(BaseUserManager):
    def create_user(self, email_address, password=None, **extra_fields):
        if not email_address:
            raise ValueError("email_required")

        email_address = self.normalize_email(email_address)

        user = self.model(
            email_address=email_address,
            **extra_fields
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email_address, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)
        extra_fields.setdefault("is_email_verified", True)

        return self.create_user(
            email_address=email_address,
            password=password,
            **extra_fields
        )


class User(AbstractBaseUser, PermissionsMixin):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    email_address = models.EmailField(unique=True)

    is_active = models.BooleanField(default=False)
    is_email_verified = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = "email_address"
    REQUIRED_FIELDS = []

    objects = UserManager()

    def __str__(self):
        return self.email_address


class OTP(models.Model):
    PURPOSE_CHOICES = (
        ("email_verify", "Email Verify"),
        ("password_reset", "Password Reset"),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="otps")
    email_address = models.EmailField()
    purpose = models.CharField(max_length=30, choices=PURPOSE_CHOICES)
    otp_code = models.CharField(max_length=6)

    attempt_count = models.PositiveIntegerField(default=0)
    resend_count = models.PositiveIntegerField(default=0)
    is_verified = models.BooleanField(default=False)

    expires_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    def is_expired(self):
        return timezone.now() >= self.expires_at