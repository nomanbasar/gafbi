from rest_framework import serializers
from .models import Product


class ProductSerializer(serializers.ModelSerializer):
    image = serializers.ImageField(write_only=True, required=False)
    image_url = serializers.SerializerMethodField()
    quantity_with_unit = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            "id",
            "image_url",
            "product_id",
            "name",
            "price",
            "quantity",
            "unit",
            "quantity_with_unit",
            "description",
            "image",
            "is_active",
            "created_at",
        ]
        read_only_fields = [
            "id",
            "product_id",
            "image_url",
            "quantity_with_unit",
            "is_active",
            "created_at",
        ]

    def get_image_url(self, obj):
        if obj.image:
            return obj.image.url
        return None

    def get_quantity_with_unit(self, obj):
        return f"{obj.quantity} {obj.unit}"