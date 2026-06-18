from django.conf import settings
from django.db import models
from django.utils.text import slugify
from ckeditor.fields import RichTextField

from apps.categories.models import Category


class ProductQuerySet(models.QuerySet):
    def published(self):
        return self.filter(status=Product.Status.PUBLISHED)


class Product(models.Model):
    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        PUBLISHED = "published", "Published"
        ARCHIVED = "archived", "Archived"

    class FormulationType(models.TextChoices):
        SC = "SC", "SC Formulation"
        EC = "EC", "EC Formulation"
        ME = "ME", "ME Formulation"
        EW = "EW", "EW Formulation"
        ADJUVANT = "ADJUVANT", "Adjuvant"
        WETTING = "WETTING", "Wetting Agent"
        DISPERSING = "DISPERSING", "Dispersing Agent"
        TEXTILE = "TEXTILE", "Textile Chemical"
        CROP_PROTECTION = "CROP_PROTECTION", "Crop Protection"
        OTHER = "OTHER", "Other"

    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name="products",
    )
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=280, unique=True, blank=True)
    product_code = models.CharField(max_length=50, blank=True, help_text="e.g. STAGSURF D33")
    short_description = models.TextField(blank=True)
    description = RichTextField(blank=True)
    technical_specifications = models.TextField(
        blank=True,
        help_text="General technical overview (structured properties managed separately).",
    )
    thumbnail = models.ImageField(
        upload_to="products/thumbnails/",
        blank=True,
        null=True,
        help_text="Used for listing cards, search results, and featured products.",
    )
    formulation_type = models.CharField(
        max_length=20,
        choices=FormulationType.choices,
        default=FormulationType.OTHER,
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.DRAFT,
    )
    is_featured = models.BooleanField(default=False)
    display_order = models.PositiveIntegerField(default=0)
    meta_title = models.CharField(max_length=255, blank=True)
    meta_description = models.TextField(blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="products_created",
    )
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="products_updated",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = ProductQuerySet.as_manager()

    class Meta:
        ordering = ["display_order", "name"]
        indexes = [
            models.Index(fields=["slug"]),
            models.Index(fields=["status", "is_featured"]),
            models.Index(fields=["formulation_type"]),
            models.Index(fields=["display_order"]),
        ]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name)
            slug = base_slug
            counter = 1
            while Product.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)


class ProductImage(models.Model):
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="images",
    )
    image = models.ImageField(upload_to="products/images/")
    alt_text = models.CharField(max_length=255, blank=True)
    is_primary = models.BooleanField(default=False)
    display_order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["display_order", "created_at"]

    def __str__(self):
        return f"{self.product.name} — Image {self.pk}"

    def save(self, *args, **kwargs):
        if self.is_primary:
            ProductImage.objects.filter(
                product=self.product, is_primary=True
            ).exclude(pk=self.pk).update(is_primary=False)
        super().save(*args, **kwargs)


class ProductProperty(models.Model):
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="properties",
    )
    property_name = models.CharField(max_length=200)
    property_value = models.CharField(max_length=500)
    display_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["display_order", "property_name"]
        verbose_name_plural = "product properties"

    def __str__(self):
        return f"{self.property_name}: {self.property_value}"


class ProductBenefit(models.Model):
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="benefits",
    )
    benefit = models.CharField(max_length=500)
    display_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["display_order", "id"]

    def __str__(self):
        return self.benefit


class ProductApplication(models.Model):
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="applications",
    )
    application_text = models.CharField(max_length=300)
    display_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["display_order", "id"]

    def __str__(self):
        return self.application_text


class ProductMetric(models.Model):
    """Future-ready analytics stub — extend for view/download tracking."""

    product = models.OneToOneField(
        Product,
        on_delete=models.CASCADE,
        related_name="metrics",
    )
    view_count = models.PositiveIntegerField(default=0)
    inquiry_count = models.PositiveIntegerField(default=0)
    download_count = models.PositiveIntegerField(default=0)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "product metrics"

    def __str__(self):
        return f"Metrics for {self.product.name}"
