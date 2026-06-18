from django.conf import settings
from django.db import models

from apps.products.models import Product


class Inquiry(models.Model):
    class Status(models.TextChoices):
        NEW = "new", "New"
        CONTACTED = "contacted", "Contacted"
        QUALIFIED = "qualified", "Qualified"
        CLOSED = "closed", "Closed"

    class Source(models.TextChoices):
        WEBSITE = "website", "Website"
        PRODUCT_PAGE = "product_page", "Product Page"
        CONTACT_PAGE = "contact_page", "Contact Page"

    name = models.CharField(max_length=200)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    company = models.CharField(max_length=255, blank=True)
    product = models.ForeignKey(
        Product,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="inquiries",
    )
    product_name = models.CharField(
        max_length=255,
        blank=True,
        help_text="Snapshot of product name at time of inquiry.",
    )
    message = models.TextField()
    source = models.CharField(
        max_length=20,
        choices=Source.choices,
        default=Source.WEBSITE,
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.NEW,
    )
    admin_notes = models.TextField(blank=True, help_text="Legacy notes field — use Inquiry Notes below.")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name_plural = "inquiries"
        indexes = [
            models.Index(fields=["status"]),
            models.Index(fields=["source"]),
            models.Index(fields=["-created_at"]),
        ]

    def __str__(self):
        return f"{self.name} — {self.get_status_display()}"

    def save(self, *args, **kwargs):
        if self.product_id and not self.product_name:
            self.product_name = self.product.name
        super().save(*args, **kwargs)


class InquiryNote(models.Model):
    inquiry = models.ForeignKey(
        Inquiry,
        on_delete=models.CASCADE,
        related_name="notes",
    )
    note = models.TextField()
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="inquiry_notes",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Note on {self.inquiry.name} — {self.created_at:%Y-%m-%d}"
