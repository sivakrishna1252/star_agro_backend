from django.db.models import Q

from apps.products.models import Product


def search_products(query):
    """Search published products by name, category, and formulation type."""
    return (
        Product.objects.published()
        .select_related("category")
        .prefetch_related("images")
        .filter(
            Q(name__icontains=query)
            | Q(product_code__icontains=query)
            | Q(short_description__icontains=query)
            | Q(category__name__icontains=query)
            | Q(formulation_type__icontains=query)
        )
        .distinct()
        .order_by("display_order", "name")
    )
