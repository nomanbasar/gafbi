from django.contrib import admin
from .models import Product


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "product_id",
        "name",
        "price",
        "quantity",
        "unit",
        "is_active",
        "created_at",
    )

    list_filter = (
        "unit",
        "is_active",
        "created_at",
    )

    search_fields = (
        "product_id",
        "name",
        "description",
    )

    readonly_fields = (
        "product_id",
        "created_at",
    )

    ordering = ("-created_at",)

    fieldsets = (
        ("Basic Information", {
            "fields": (
                "product_id",
                "name",
                "price",
                "quantity",
                "unit",
                "description",
                "image",
                "is_active",
            )
        }),
        ("Date Information", {
            "fields": (
                "created_at",
            )
        }),
    )