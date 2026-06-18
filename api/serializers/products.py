from rest_framework import serializers

from apps.documents.models import ProductDocument
from apps.products.models import (
    Product,
    ProductApplication,
    ProductBenefit,
    ProductImage,
    ProductProperty,
)
from api.serializers.product_utils import get_product_card_image


class ProductImageSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = ProductImage
        fields = ["id", "image", "image_url", "alt_text", "is_primary", "display_order"]

    def get_image_url(self, obj):
        request = self.context.get("request")
        if request:
            return request.build_absolute_uri(obj.image.url)
        return obj.image.url


class ProductPropertySerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductProperty
        fields = ["id", "property_name", "property_value", "display_order"]


class ProductBenefitSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductBenefit
        fields = ["id", "benefit", "display_order"]


class ProductApplicationSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductApplication
        fields = ["id", "application_text", "display_order"]


class ProductDocumentSerializer(serializers.ModelSerializer):
    file_url = serializers.SerializerMethodField()

    class Meta:
        model = ProductDocument
        fields = [
            "id",
            "document_name",
            "document_type",
            "file_url",
            "display_order",
        ]

    def get_file_url(self, obj):
        request = self.context.get("request")
        if request:
            return request.build_absolute_uri(obj.file.url)
        return obj.file.url


class ProductListSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source="category.name", read_only=True)
    category_slug = serializers.CharField(source="category.slug", read_only=True)
    thumbnail_url = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            "id",
            "name",
            "slug",
            "product_code",
            "short_description",
            "category_name",
            "category_slug",
            "formulation_type",
            "is_featured",
            "display_order",
            "meta_title",
            "meta_description",
            "thumbnail_url",
        ]

    def get_thumbnail_url(self, obj):
        return get_product_card_image(obj, self.context.get("request"))


class ProductDetailSerializer(serializers.ModelSerializer):
    category = serializers.SerializerMethodField()
    thumbnail_url = serializers.SerializerMethodField()
    images = ProductImageSerializer(many=True, read_only=True)
    properties = ProductPropertySerializer(many=True, read_only=True)
    benefits = ProductBenefitSerializer(many=True, read_only=True)
    applications = ProductApplicationSerializer(many=True, read_only=True)
    documents = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            "id",
            "name",
            "slug",
            "product_code",
            "short_description",
            "description",
            "technical_specifications",
            "formulation_type",
            "is_featured",
            "display_order",
            "category",
            "thumbnail_url",
            "images",
            "properties",
            "benefits",
            "applications",
            "documents",
            "meta_title",
            "meta_description",
            "created_at",
            "updated_at",
        ]

    def get_category(self, obj):
        return {
            "id": obj.category.id,
            "name": obj.category.name,
            "slug": obj.category.slug,
            "meta_title": obj.category.meta_title,
            "meta_description": obj.category.meta_description,
        }

    def get_thumbnail_url(self, obj):
        return get_product_card_image(obj, self.context.get("request"))

    def get_documents(self, obj):
        docs = obj.documents.filter(is_active=True)
        return ProductDocumentSerializer(docs, many=True, context=self.context).data
