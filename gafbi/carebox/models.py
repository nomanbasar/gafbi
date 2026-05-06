from django.db import models
from django.conf import settings
from products.models import Product


class CareBoxApplication(models.Model):
    STATUS_CHOICES = (
        ("pending", "Pending"),
        ("approved", "Approved"),
        ("rejected", "Rejected"),
        ("delivered", "Delivered"),
        ("cancelled", "Cancelled"),
    )

    GENDER_CHOICES = (
        ("mister", "Mister"),
        ("woman", "Woman"),
        ("diverse", "Diverse"),
    )

    INSURANCE_TYPE_CHOICES = (
        ("legally_insured", "Legally Insured"),
        ("privately_insured", "Privately Insured"),
        ("local_social_welfare_office", "Local/Social Welfare Office"),
    )

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="carebox_applications")

    gender = models.CharField(max_length=20, choices=GENDER_CHOICES)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    date_of_birth = models.DateField()
    level_of_care = models.PositiveSmallIntegerField()

    street_address = models.CharField(max_length=255)
    area = models.CharField(max_length=120)
    city = models.CharField(max_length=120)
    zip_code = models.CharField(max_length=20)

    different_delivery_address = models.BooleanField(default=False)
    delivery_street_address = models.CharField(max_length=255, blank=True, null=True)
    delivery_area = models.CharField(max_length=120, blank=True, null=True)
    delivery_city = models.CharField(max_length=120, blank=True, null=True)
    delivery_zip_code = models.CharField(max_length=20, blank=True, null=True)

    email = models.EmailField()
    phone_number = models.CharField(max_length=30)

    consultation_answer = models.CharField(max_length=255)
    consultation_reason = models.TextField(blank=True, null=True)
    already_provided_with_care_aids = models.BooleanField(default=False)

    insurance_type = models.CharField(max_length=50, choices=INSURANCE_TYPE_CHOICES)
    insurance_name = models.CharField(max_length=255, blank=True, null=True)
    insurance_number = models.CharField(max_length=100, blank=True, null=True)

    signature = models.TextField(blank=True, null=True)
    signed_cost_assumption = models.BooleanField(default=False)
    signed_supplier_change = models.BooleanField(default=False)

    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    application_month = models.CharField(max_length=7)

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    admin_note = models.TextField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.application_month}"


class CareBoxApplicationItem(models.Model):
    application = models.ForeignKey(CareBoxApplication, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.product.name} x {self.quantity}"


class CareBoxFeedback(models.Model):
    application = models.ForeignKey(CareBoxApplication, on_delete=models.CASCADE, related_name="feedbacks", blank=True, null=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="carebox_feedbacks", blank=True, null=True)

    satisfaction = models.CharField(max_length=50)
    information_helpful = models.BooleanField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.satisfaction