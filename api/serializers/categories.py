from drf_spectacular.utils import extend_schema, extend_schema_field
from rest_framework import serializers

from apps.categories.models import Category
from apps.products.models import Product


class CategorySerializer(serializers.ModelSerializer):
    product_count = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = [
            "id",
            "name",
            "slug",
            "description",
            "image",
            "display_order",
            "meta_title",
            "meta_description",
            "product_count",
        ]

    @extend_schema_field(serializers.IntegerField())
    def get_product_count(self, obj):
        return obj.products.filter(status=Product.Status.PUBLISHED).count()
