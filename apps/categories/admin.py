from django.contrib import admin

from .models import Category


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "is_active", "display_order", "updated_at")
    list_filter = ("is_active",)
    search_fields = ("name", "description")
    prepopulated_fields = {"slug": ("name",)}
    list_editable = ("is_active", "display_order")
    ordering = ("display_order", "name")
    fieldsets = (
        (
            None,
            {"fields": ("name", "slug", "description", "image", "is_active", "display_order")},
        ),
        (
            "SEO",
            {"fields": ("meta_title", "meta_description"), "classes": ("collapse",)},
        ),
    )
