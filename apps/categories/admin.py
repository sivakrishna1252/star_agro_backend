from django.contrib import admin
from django.db.models import Count, Q
from django.urls import reverse
from django.utils.html import format_html

from apps.products.models import Product

from .models import Category


class CategoryProductInline(admin.TabularInline):
    model = Product
    extra = 0
    fields = ("name", "product_code", "status", "is_featured", "display_order")
    show_change_link = True
    ordering = ("display_order", "name")
    verbose_name = "Product"
    verbose_name_plural = "Products in this category"


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "slug",
        "product_count",
        "published_product_count",
        "is_active",
        "display_order",
        "updated_at",
    )
    list_filter = ("is_active",)
    search_fields = ("name", "description")
    prepopulated_fields = {"slug": ("name",)}
    list_editable = ("is_active", "display_order")
    ordering = ("display_order", "name")
    inlines = [CategoryProductInline]
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

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.annotate(
            _product_count=Count("products", distinct=True),
            _published_product_count=Count(
                "products",
                filter=Q(products__status=Product.Status.PUBLISHED),
                distinct=True,
            ),
        )

    @admin.display(description="Products", ordering="_product_count")
    def product_count(self, obj):
        count = obj._product_count
        if count == 0:
            return "0"
        url = (
            f"{reverse('admin:products_product_changelist')}?category__id__exact={obj.pk}"
        )
        return format_html('<a href="{}">{}</a>', url, count)

    @admin.display(description="Published", ordering="_published_product_count")
    def published_product_count(self, obj):
        total = obj._product_count
        published = obj._published_product_count
        if published == 0:
            return format_html('<span style="color: #999;">0</span>')
        if published < total:
            return format_html(
                '<span style="color: #856404;" title="{} draft/archived">{}</span>',
                total - published,
                published,
            )
        return published
