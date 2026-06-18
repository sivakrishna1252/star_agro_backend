from django.db import models

from apps.products.models import Product


class ProductDocument(models.Model):
    class DocumentType(models.TextChoices):
        TDS = "TDS", "Technical Data Sheet"
        BROCHURE = "BROCHURE", "Brochure"
        CATALOG = "CATALOG", "Catalog"
        MSDS = "MSDS", "MSDS"
        PRODUCT_SHEET = "PRODUCT_SHEET", "Product Sheet"

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="documents",
    )
    document_name = models.CharField(max_length=255)
    document_type = models.CharField(
        max_length=20,
        choices=DocumentType.choices,
        default=DocumentType.TDS,
    )
    file = models.FileField(upload_to="documents/products/")
    is_active = models.BooleanField(default=True)
    display_order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["display_order", "document_name"]
        indexes = [models.Index(fields=["document_type"])]

    def __str__(self):
        return self.document_name


class CompanyDocument(models.Model):
    class DocumentType(models.TextChoices):
        COMPANY_PROFILE = "COMPANY_PROFILE", "Company Profile"
        COMPANY_BROCHURE = "COMPANY_BROCHURE", "Company Brochure"
        CERTIFICATE = "CERTIFICATE", "Certificate"
        TECHNICAL_CATALOG = "TECHNICAL_CATALOG", "Technical Catalog"
        OTHER = "OTHER", "Other"

    title = models.CharField(max_length=255)
    document_type = models.CharField(
        max_length=30,
        choices=DocumentType.choices,
        default=DocumentType.OTHER,
    )
    pdf_file = models.FileField(upload_to="documents/company/")
    display_order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["display_order", "title"]

    def __str__(self):
        return self.title


class DocumentDownloadLog(models.Model):
    """Future-ready download analytics — extend with user/session tracking."""

    document = models.ForeignKey(
        ProductDocument,
        on_delete=models.CASCADE,
        related_name="download_logs",
    )
    downloaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-downloaded_at"]

    def __str__(self):
        return f"Download: {self.document.document_name} at {self.downloaded_at}"
