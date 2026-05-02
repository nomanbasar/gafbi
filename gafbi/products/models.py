from django.db import models


class Product(models.Model):
    UNIT_CHOICES = (
        ("ml", "ml"),
        ("pcs", "pcs"),
        ("box", "box"),
    )

    product_id = models.CharField(max_length=30, unique=True, blank=True)
    name = models.CharField(max_length=255)

    price = models.DecimalField(max_digits=10, decimal_places=2)

    quantity = models.DecimalField(max_digits=10, decimal_places=2)
    unit = models.CharField(max_length=20, choices=UNIT_CHOICES)

    description = models.TextField()
    image = models.ImageField(upload_to="products/", blank=True, null=True)

    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.product_id:
            last = Product.objects.order_by("-id").first()
            num = 1 if not last else last.id + 1
            self.product_id = f"DS-{num:06d}"
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name