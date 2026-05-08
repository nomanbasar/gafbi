from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import User, OTP


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    ordering = ["-created_at"]
    list_display = ["email_address", "is_email_verified", "name", "image", "is_active", "is_staff", "created_at"]
    search_fields = ["email_address"]

    fieldsets = (
        (None, {"fields": ("email_address", "password")}),
        ("Status", {"fields": ("is_active", "is_email_verified", "is_staff", "is_superuser")}),
        ("Permissions", {"fields": ("groups", "user_permissions")}),
        ("Dates", {"fields": ("last_login",)}),
    )

    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": ("email_address", "password1", "password2", "is_staff", "is_superuser", "is_active", "is_email_verified"),
        }),
    )


@admin.register(OTP)
class OTPAdmin(admin.ModelAdmin):
    list_display = ["email_address", "purpose", "otp_code", "is_verified", "attempt_count", "expires_at", "created_at"]
    search_fields = ["email_address", "otp_code"]
    list_filter = ["purpose", "is_verified"]