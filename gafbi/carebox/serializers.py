from decimal import Decimal
from django.utils import timezone
from rest_framework import serializers
from authentication.models import User
from products.models import Product
from products.serializers import ProductSerializer
from .models import CareBoxApplication, CareBoxApplicationItem, CareBoxFeedback
import calendar

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
            "gender",
            "first_name",
            "last_name",
            "date_of_birth",
            "level_of_care",
            "street_address",
            "area",
            "city",
            "zip_code",
            "different_delivery_address",
            "email",
            "phone_number",
            "consultation_answer",
            "consultation_reason",
            "already_provided_with_care_aids",
            "insurance_type",
            "insurance_name",
            "insurance_number",
            "signature",
            "signed_cost_assumption",
            "signed_supplier_change",
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
    satisfaction = serializers.ChoiceField(choices=[
        "very_satisfied",
        "satisfied",
        "ok",
        "dissatisfied",
        "very_dissatisfied",
    ])

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

    def validate(self, attrs):
        request = self.context.get("request")
        application = attrs.get("application")

        if application and request.user.is_authenticated:
            if application.user != request.user:
                raise serializers.ValidationError(
                    "This application does not belong to you"
                )

        return attrs

    def create(self, validated_data):
        request = self.context.get("request")

        if request and request.user and request.user.is_authenticated:
            validated_data["user"] = request.user

        return super().create(validated_data)

class AdminCareBoxStatusSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=["pending", "approved", "rejected", "delivered", "cancelled"])
    admin_note = serializers.CharField(required=False, allow_blank=True, allow_null=True)



class AdminDashboardUserSerializer(serializers.ModelSerializer):
    user_id = serializers.SerializerMethodField()
    name = serializers.SerializerMethodField()
    register_email = serializers.EmailField(source="email_address")
    joined = serializers.DateTimeField(source="created_at")
    care_level = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            "id",
            "user_id",
            "name",
            "register_email",
            "joined",
            "care_level",
        ]

    def get_user_id(self, obj):
        return f"@{obj.email_address.split('@')[0]}"

    def get_name(self, obj):
        application = obj.carebox_applications.order_by("-created_at").first()
        if application:
            return f"{application.first_name} {application.last_name}"
        return obj.email_address.split("@")[0]

    def get_care_level(self, obj):
        application = obj.carebox_applications.order_by("-created_at").first()
        if application:
            return application.level_of_care
        return None


class AdminDashboardOrderListSerializer(serializers.ModelSerializer):
    order_id = serializers.SerializerMethodField()
    order_date = serializers.DateTimeField(source="created_at")
    customer = serializers.SerializerMethodField()
    shipping_carrier = serializers.SerializerMethodField()
    shipment_status = serializers.SerializerMethodField()

    class Meta:
        model = CareBoxApplication
        fields = [
            "id",
            "order_id",
            "order_date",
            "customer",
            "email",
            "shipping_carrier",
            "shipment_status",
            "status",
        ]

    def get_order_id(self, obj):
        return f"DS-{obj.id}"

    def get_customer(self, obj):
        return f"{obj.first_name} {obj.last_name}"

    def get_shipping_carrier(self, obj):
        return obj.shipping_carrier or "N/A"

    def get_shipment_status(self, obj):
        if obj.status == "delivered":
            return "shipped"
        if obj.status == "cancelled":
            return "cancelled"
        return "unshipped"


class AdminDashboardOrderDetailsSerializer(serializers.ModelSerializer):
    order_id = serializers.SerializerMethodField()
    order_date = serializers.DateTimeField(source="created_at")
    delivery_date = serializers.DateTimeField(source="shipped_at", allow_null=True)
    customer_name = serializers.SerializerMethodField()
    shipping_address = serializers.SerializerMethodField()
    items = CareBoxApplicationItemSerializer(many=True, read_only=True)

    class Meta:
        model = CareBoxApplication
        fields = [
            "id",
            "order_id",
            "order_date",
            "delivery_date",
            "customer_name",
            "email",
            "phone_number",
            "shipping_address",
            "total_amount",
            "status",
            "shipping_carrier",
            "tracking_number",
            "shipped_quantity",
            "items",
        ]

    def get_order_id(self, obj):
        return f"DS-{obj.id}"

    def get_customer_name(self, obj):
        return f"{obj.first_name} {obj.last_name}"

    def get_shipping_address(self, obj):
        if obj.different_delivery_address:
            return {
                "street_address": obj.delivery_street_address,
                "area": obj.delivery_area,
                "city": obj.delivery_city,
                "zip_code": obj.delivery_zip_code,
            }

        return {
            "street_address": obj.street_address,
            "area": obj.area,
            "city": obj.city,
            "zip_code": obj.zip_code,
        }


class AdminConfirmShipmentSerializer(serializers.Serializer):
    shipping_carrier = serializers.CharField(max_length=100)
    tracking_number = serializers.CharField(max_length=100)
    shipped_quantity = serializers.IntegerField(min_value=1)


class AdminDashboardApplicationListSerializer(serializers.ModelSerializer):
    application_date = serializers.DateTimeField(source="created_at")
    customer = serializers.SerializerMethodField()

    class Meta:
        model = CareBoxApplication
        fields = [
            "id",
            "application_date",
            "customer",
            "email",
            "status",
        ]

    def get_customer(self, obj):
        return f"{obj.first_name} {obj.last_name}"


class AdminDashboardApplicationDetailsSerializer(serializers.ModelSerializer):
    customer = serializers.SerializerMethodField()
    items = CareBoxApplicationItemSerializer(many=True, read_only=True)

    class Meta:
        model = CareBoxApplication
        fields = [
            "id",
            "customer",
            "status",
            "admin_note",
            "gender",
            "first_name",
            "last_name",
            "date_of_birth",
            "level_of_care",
            "street_address",
            "area",
            "city",
            "zip_code",
            "different_delivery_address",
            "delivery_street_address",
            "delivery_area",
            "delivery_city",
            "delivery_zip_code",
            "email",
            "phone_number",
            "consultation_answer",
            "consultation_reason",
            "already_provided_with_care_aids",
            "insurance_type",
            "insurance_name",
            "insurance_number",
            "signature",
            "signed_cost_assumption",
            "signed_supplier_change",
            "total_amount",
            "application_month",
            "created_at",
            "items",
        ]

    def get_customer(self, obj):
        return f"{obj.first_name} {obj.last_name}"


class AdminApplicationDecisionSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=["approved", "rejected"])
    admin_note = serializers.CharField(required=False, allow_blank=True, allow_null=True)



def get_month_name(application_month):
    if not application_month:
        return None

    try:
        year, month = application_month.split("-")
        return f"{calendar.month_name[int(month)]} {year}"
    except Exception:
        return application_month


class UserDashboardOverviewItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source="product.name", read_only=True)
    product_image_url = serializers.SerializerMethodField()
    quantity_with_unit = serializers.SerializerMethodField()

    class Meta:
        model = CareBoxApplicationItem
        fields = [
            "id",
            "product",
            "product_name",
            "product_image_url",
            "quantity",
            "quantity_with_unit",
        ]

    def get_product_image_url(self, obj):
        if obj.product.image:
            return obj.product.image.url
        return None

    def get_quantity_with_unit(self, obj):
        quantity = getattr(obj.product, "quantity", None)
        unit = getattr(obj.product, "unit", None)

        if quantity and unit:
            return f"{quantity} {unit}"

        if quantity:
            return str(quantity)

        return None


class UserDashboardOverviewApplicationSerializer(serializers.ModelSerializer):
    month = serializers.SerializerMethodField()
    items = UserDashboardOverviewItemSerializer(many=True, read_only=True)

    class Meta:
        model = CareBoxApplication
        fields = [
            "id",
            "month",
            "status",
            "application_month",
            "created_at",
            "items",
        ]

    def get_month(self, obj):
        return get_month_name(obj.application_month)


class UserDashboardDeliveryAddressSerializer(serializers.ModelSerializer):
    current_address = serializers.SerializerMethodField()

    class Meta:
        model = CareBoxApplication
        fields = [
            "id",
            "current_address",
            "street_address",
            "area",
            "city",
            "zip_code",
            "email",
            "phone_number",
        ]

    def get_current_address(self, obj):
        return {
            "name": f"{obj.first_name} {obj.last_name}",
            "street_address": obj.street_address,
            "area": obj.area,
            "city": obj.city,
            "zip_code": obj.zip_code,
            "email": obj.email,
            "phone_number": obj.phone_number,
        }


class UserDashboardDeliveryAddressUpdateSerializer(serializers.Serializer):
    street_address = serializers.CharField(max_length=255, required=False)
    area = serializers.CharField(max_length=120, required=False)
    city = serializers.CharField(max_length=120, required=False)
    zip_code = serializers.CharField(max_length=20, required=False)
    email = serializers.EmailField(required=False)
    phone_number = serializers.CharField(max_length=30, required=False)


class UserDashboardPersonalDataSerializer(serializers.ModelSerializer):
    gender = serializers.SerializerMethodField()

    class Meta:
        model = CareBoxApplication
        fields = [
            "id",
            "gender",
            "first_name",
            "last_name",
            "date_of_birth",
            "level_of_care",
        ]

    def get_gender(self, obj):
        if obj.gender == "diverse":
            return "divers"
        return obj.gender


class UserDashboardPersonalDataUpdateSerializer(serializers.Serializer):
    gender = serializers.ChoiceField(
        choices=["mister", "woman", "divers", "diverse"],
        required=False
    )
    first_name = serializers.CharField(max_length=100, required=False)
    last_name = serializers.CharField(max_length=100, required=False)
    date_of_birth = serializers.DateField(required=False)
    level_of_care = serializers.IntegerField(min_value=1, max_value=10, required=False)

    def validate_gender(self, value):
        if value == "divers":
            return "diverse"
        return value