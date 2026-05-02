from rest_framework import serializers
from .models import Product


class ProductSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()
    quantity_with_unit = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            "id",
            "product_id",
            "name",
            "price",
            "quantity",
            "unit",
            "quantity_with_unit",
            "description",
            "image",
            "image_url",
            "is_active",
            "created_at",
        ]
        read_only_fields = ["id", "product_id", "image_url", "created_at"]

    def get_image_url(self, obj):
        request = self.context.get("request")
        if obj.image and request:
            return request.build_absolute_uri(obj.image.url)
        return None

    def get_quantity_with_unit(self, obj):
        return f"{obj.quantity} {obj.unit}"