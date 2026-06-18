from django.contrib import admin

from apps.documents.models import ProductDocument

from .models import (
    Product,
    ProductApplication,
    ProductBenefit,
    ProductImage,
    ProductMetric,
    ProductProperty,
)


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1
    fields = ("image", "alt_text", "is_primary", "display_order")
    ordering = ("display_order",)


class ProductPropertyInline(admin.TabularInline):
    model = ProductProperty
    extra = 1
    fields = ("property_name", "property_value", "display_order")
    ordering = ("display_order",)


class ProductBenefitInline(admin.TabularInline):
    model = ProductBenefit
    extra = 1
    fields = ("benefit", "display_order")
    ordering = ("display_order",)


class ProductApplicationInline(admin.TabularInline):
    model = ProductApplication
    extra = 1
    fields = ("application_text", "display_order")
    ordering = ("display_order",)


class ProductDocumentInline(admin.TabularInline):
    model = ProductDocument
    extra = 1
    fields = ("document_name", "document_type", "file", "is_active", "display_order")
    ordering = ("display_order",)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "product_code",
        "category",
        "formulation_type",
        "status",
        "is_featured",
        "display_order",
        "created_by",
        "updated_at",
    )
    list_filter = ("status", "category", "formulation_type", "is_featured")
    search_fields = ("name", "product_code", "slug", "description")
    prepopulated_fields = {"slug": ("name",)}
    list_editable = ("status", "is_featured", "display_order")
    autocomplete_fields = ("category",)
    readonly_fields = ("created_by", "updated_by", "created_at", "updated_at")
    inlines = [
        ProductImageInline,
        ProductPropertyInline,
        ProductBenefitInline,
        ProductApplicationInline,
        ProductDocumentInline,
    ]
    fieldsets = (
        (
            "Basic Information",
            {
                "fields": (
                    "category",
                    "name",
                    "slug",
                    "product_code",
                    "formulation_type",
                    "status",
                    "is_featured",
                    "display_order",
                    "thumbnail",
                )
            },
        ),
        (
            "Content",
            {
                "fields": (
                    "short_description",
                    "description",
                    "technical_specifications",
                )
            },
        ),
        (
            "SEO",
            {"fields": ("meta_title", "meta_description"), "classes": ("collapse",)},
        ),
        (
            "Audit",
            {
                "fields": ("created_by", "updated_by", "created_at", "updated_at"),
                "classes": ("collapse",),
            },
        ),
    )

    def save_model(self, request, obj, form, change):
        if not change:
            obj.created_by = request.user
        obj.updated_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ("product", "alt_text", "is_primary", "display_order", "created_at")
    list_filter = ("is_primary",)
    list_editable = ("display_order", "is_primary")
    search_fields = ("product__name", "alt_text")
    autocomplete_fields = ("product",)
    ordering = ("product", "display_order")


@admin.register(ProductProperty)
class ProductPropertyAdmin(admin.ModelAdmin):
    list_display = ("product", "property_name", "property_value", "display_order")
    list_editable = ("display_order",)
    search_fields = ("product__name", "property_name")
    autocomplete_fields = ("product",)


@admin.register(ProductBenefit)
class ProductBenefitAdmin(admin.ModelAdmin):
    list_display = ("product", "benefit", "display_order")
    list_editable = ("display_order",)
    search_fields = ("product__name", "benefit")
    autocomplete_fields = ("product",)


@admin.register(ProductApplication)
class ProductApplicationAdmin(admin.ModelAdmin):
    list_display = ("product", "application_text", "display_order")
    list_editable = ("display_order",)
    search_fields = ("product__name", "application_text")
    autocomplete_fields = ("product",)


@admin.register(ProductMetric)
class ProductMetricAdmin(admin.ModelAdmin):
    list_display = ("product", "view_count", "inquiry_count", "download_count", "updated_at")
    readonly_fields = ("updated_at",)
    autocomplete_fields = ("product",)
