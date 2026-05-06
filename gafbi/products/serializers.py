from rest_framework import serializers
from .models import Product, ProductReview
from django.db.models import Avg

class ProductReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductReview
        fields = [
            "id",
            "name",
            "email",
            "rating",
            "review",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]

    def validate_rating(self, value):
        if value < 1 or value > 5:
            raise serializers.ValidationError("Rating must be between 1 and 5")
        return value


class ProductSerializer(serializers.ModelSerializer):
    image = serializers.ImageField(write_only=True, required=False)
    image_url = serializers.SerializerMethodField()
    quantity_with_unit = serializers.SerializerMethodField()
    average_rating = serializers.SerializerMethodField()
    total_reviews = serializers.SerializerMethodField()

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
            "average_rating",
            "total_reviews",
            "created_at",
        ]
        read_only_fields = [
            "id",
            "product_id",
            "image_url",
            "quantity_with_unit",
            "is_active",
            "average_rating",
            "total_reviews",
            "created_at",
        ]

    def get_image_url(self, obj):
        if obj.image:
            return obj.image.url
        return None

    def get_quantity_with_unit(self, obj):
        return f"{obj.quantity} {obj.unit}"
    
    def get_average_rating(self, obj):
        avg = obj.reviews.filter(is_active=True).aggregate(avg=Avg("rating"))["avg"]
        return round(avg, 1) if avg else 0

    def get_total_reviews(self, obj):
        return obj.reviews.filter(is_active=True).count()


class ProductDetailSerializer(ProductSerializer):
    reviews = serializers.SerializerMethodField()
    rating_breakdown = serializers.SerializerMethodField()

    class Meta(ProductSerializer.Meta):
        fields = ProductSerializer.Meta.fields + [
            "rating_breakdown",
            "reviews",
        ]

    def get_reviews(self, obj):
        reviews = obj.reviews.filter(is_active=True)
        return ProductReviewSerializer(reviews, many=True).data

    def get_rating_breakdown(self, obj):
        reviews = obj.reviews.filter(is_active=True)

        return {
            "5": reviews.filter(rating=5).count(),
            "4": reviews.filter(rating=4).count(),
            "3": reviews.filter(rating=3).count(),
            "2": reviews.filter(rating=2).count(),
            "1": reviews.filter(rating=1).count(),
        } 