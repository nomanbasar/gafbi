from django.contrib import admin
from .models import CareBoxApplication, CareBoxApplicationItem, CareBoxFeedback


class CareBoxApplicationItemInline(admin.TabularInline):
    model = CareBoxApplicationItem
    extra = 0
    readonly_fields = ["product", "quantity", "unit_price", "subtotal"]


@admin.register(CareBoxApplication)
class CareBoxApplicationAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "user",
        "first_name",
        "last_name",
        "level_of_care",
        "total_amount",
        "application_month",
        "status",
        "created_at",
    ]
    list_filter = ["status", "application_month", "level_of_care", "created_at"]
    search_fields = ["first_name", "last_name", "email", "phone_number"]
    inlines = [CareBoxApplicationItemInline]


@admin.register(CareBoxFeedback)
class CareBoxFeedbackAdmin(admin.ModelAdmin):
    list_display = ["id", "application", "user", "satisfaction", "information_helpful", "created_at"]