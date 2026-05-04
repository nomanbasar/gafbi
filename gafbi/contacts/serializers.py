from rest_framework import serializers
from .models import ContactMessage


class ContactMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactMessage
        fields = [
            "id",
            "first_name",
            "last_name",
            "email",
            "telephone_number",
            "regarding",
            "news",
            "is_read",
            "created_at",
        ]
        read_only_fields = ["id", "is_read", "created_at"]