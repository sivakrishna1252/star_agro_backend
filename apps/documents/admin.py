from django.contrib import admin

from .models import CompanyDocument, DocumentDownloadLog, ProductDocument


@admin.register(ProductDocument)
class ProductDocumentAdmin(admin.ModelAdmin):
    list_display = (
        "document_name",
        "document_type",
        "product",
        "is_active",
        "display_order",
        "created_at",
    )
    list_filter = ("document_type", "is_active")
    search_fields = ("document_name", "product__name")
    autocomplete_fields = ("product",)
    list_editable = ("is_active", "display_order")
    ordering = ("display_order", "document_name")


@admin.register(CompanyDocument)
class CompanyDocumentAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "document_type",
        "display_order",
        "is_active",
        "created_at",
    )
    list_filter = ("document_type", "is_active")
    search_fields = ("title",)
    list_editable = ("display_order", "is_active")
    ordering = ("display_order", "title")


@admin.register(DocumentDownloadLog)
class DocumentDownloadLogAdmin(admin.ModelAdmin):
    list_display = ("document", "downloaded_at")
    list_filter = ("downloaded_at",)
    readonly_fields = ("document", "downloaded_at")
    autocomplete_fields = ("document",)

    def has_add_permission(self, request):
        return False
