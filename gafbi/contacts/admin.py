from django.contrib import admin
from .models import ContactMessage


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "first_name",
        "last_name",
        "email",
        "telephone_number",
        "regarding",
        "is_read",
        "created_at",
    )

    list_filter = (
        "is_read",
        "created_at",
    )

    search_fields = (
        "first_name",
        "last_name",
        "email",
        "telephone_number",
        "regarding",
        "news",
    )

    readonly_fields = (
        "created_at",
    )

    ordering = ("-created_at",)