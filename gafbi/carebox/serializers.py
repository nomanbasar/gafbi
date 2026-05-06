from decimal import Decimal
from django.utils import timezone
from rest_framework import serializers

from products.models import Product
from products.serializers import ProductSerializer
from .models import CareBoxApplication, CareBoxApplicationItem, CareBoxFeedback


MAX_TOTAL_AMOUNT = Decimal("42.00")
MAX_ITEMS = 6


class CareLevelSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()


class CareBoxProductSerializer(ProductSerializer):
    pass


class CareBoxApplicationItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source="product.name", read_only=True)
    product_image_url = serializers.SerializerMethodField()
    quantity_with_unit = serializers.CharField(source="product.quantity_with_unit", read_only=True)

    class Meta:
        model = CareBoxApplicationItem
        fields = [
            "id",
            "product",
            "product_name",
            "product_image_url",
            "quantity",
            "unit_price",
            "subtotal",
            "quantity_with_unit",
        ]

    def get_product_image_url(self, obj):
        if obj.product.image:
            return obj.product.image.url
        return None


class CareBoxApplicationListSerializer(serializers.ModelSerializer):
    items = CareBoxApplicationItemSerializer(many=True, read_only=True)

    class Meta:
        model = CareBoxApplication
        fields = [
            "id",
            "status",
            "first_name",
            "last_name",
            "level_of_care",
            "total_amount",
            "application_month",
            "created_at",
            "items",
        ]


class CareBoxApplicationCreateSerializer(serializers.Serializer):
    products = serializers.ListField(child=serializers.DictField(), min_length=1)

    gender = serializers.ChoiceField(choices=["mister", "woman", "diverse"])
    first_name = serializers.CharField(max_length=100)
    last_name = serializers.CharField(max_length=100)
    date_of_birth = serializers.DateField()
    level_of_care = serializers.IntegerField(min_value=1, max_value=10)

    street_address = serializers.CharField(max_length=255)
    area = serializers.CharField(max_length=120)
    city = serializers.CharField(max_length=120)
    zip_code = serializers.CharField(max_length=20)

    different_delivery_address = serializers.BooleanField(default=False)
    delivery_street_address = serializers.CharField(max_length=255, required=False, allow_blank=True, allow_null=True)
    delivery_area = serializers.CharField(max_length=120, required=False, allow_blank=True, allow_null=True)
    delivery_city = serializers.CharField(max_length=120, required=False, allow_blank=True, allow_null=True)
    delivery_zip_code = serializers.CharField(max_length=20, required=False, allow_blank=True, allow_null=True)

    email = serializers.EmailField()
    phone_number = serializers.CharField(max_length=30)

    consultation_answer = serializers.CharField(max_length=255)
    consultation_reason = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    already_provided_with_care_aids = serializers.BooleanField(default=False)

    insurance_type = serializers.ChoiceField(choices=[
        "legally_insured",
        "privately_insured",
        "local_social_welfare_office",
    ])
    insurance_name = serializers.CharField(max_length=255, required=False, allow_blank=True, allow_null=True)
    insurance_number = serializers.CharField(max_length=100, required=False, allow_blank=True, allow_null=True)

    signature = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    signed_cost_assumption = serializers.BooleanField()
    signed_supplier_change = serializers.BooleanField(default=False)

    def validate_products(self, products):
        if len(products) > MAX_ITEMS:
            raise serializers.ValidationError("You can add up to 6 items to your box")

        cleaned_products = []
        total_amount = Decimal("0.00")

        for item in products:
            product_id = item.get("product_id")
            quantity = item.get("quantity", 1)

            if not product_id:
                raise serializers.ValidationError("product_id is required")

            try:
                quantity = int(quantity)
            except Exception:
                raise serializers.ValidationError("Invalid quantity")

            if quantity < 1:
                raise serializers.ValidationError("Quantity must be at least 1")

            product = Product.objects.filter(id=product_id, is_active=True).first()
            if not product:
                raise serializers.ValidationError("Product not found")

            subtotal = product.price * quantity
            total_amount += subtotal

            cleaned_products.append({
                "product": product,
                "quantity": quantity,
                "unit_price": product.price,
                "subtotal": subtotal,
            })

        if total_amount > MAX_TOTAL_AMOUNT:
            raise serializers.ValidationError("You cannot select products more than 42 euro")

        self.context["total_amount"] = total_amount
        self.context["cleaned_products"] = cleaned_products

        return products

    def validate(self, attrs):
        request = self.context["request"]
        user = request.user
        current_month = timezone.now().strftime("%Y-%m")

        already_exists = CareBoxApplication.objects.filter(
            user=user,
            application_month=current_month
        ).exclude(status="cancelled").exists()

        if already_exists:
            raise serializers.ValidationError("You can collect only one care box per month")

        if attrs.get("different_delivery_address"):
            required_fields = [
                "delivery_street_address",
                "delivery_area",
                "delivery_city",
                "delivery_zip_code",
            ]
            for field in required_fields:
                if not attrs.get(field):
                    raise serializers.ValidationError("Delivery address is required")

        if not attrs.get("signed_cost_assumption"):
            raise serializers.ValidationError("Cost assumption signature is required")

        attrs["application_month"] = current_month
        return attrs

    def create(self, validated_data):
        request = self.context["request"]
        user = request.user

        products_data = self.context["cleaned_products"]
        total_amount = self.context["total_amount"]

        validated_data.pop("products")

        application = CareBoxApplication.objects.create(
            user=user,
            total_amount=total_amount,
            **validated_data
        )

        for item in products_data:
            CareBoxApplicationItem.objects.create(
                application=application,
                product=item["product"],
                quantity=item["quantity"],
                unit_price=item["unit_price"],
                subtotal=item["subtotal"],
            )

        return application


class CareBoxFeedbackSerializer(serializers.ModelSerializer):
    class Meta:
        model = CareBoxFeedback
        fields = [
            "id",
            "application",
            "satisfaction",
            "information_helpful",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]

    def create(self, validated_data):
        request = self.context.get("request")
        if request and request.user and request.user.is_authenticated:
            validated_data["user"] = request.user
        return super().create(validated_data)


class AdminCareBoxStatusSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=["pending", "approved", "rejected", "delivered", "cancelled"])
    admin_note = serializers.CharField(required=False, allow_blank=True, allow_null=True)