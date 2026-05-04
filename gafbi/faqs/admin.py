from django.contrib import admin
from .models import FAQ


@admin.register(FAQ)
class FAQAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "question",
        "is_active",
        "order",
        "created_at",
    )

    list_filter = (
        "is_active",
        "created_at",
    )

    search_fields = (
        "question",
        "answer",
    )

    ordering = (
        "order",
        "-created_at",
    )

    readonly_fields = (
        "created_at",
    )