import re

from rest_framework import serializers

from apps.inquiries.models import Inquiry
from apps.products.models import Product


class InquiryCreateSerializer(serializers.ModelSerializer):
    product_slug = serializers.SlugField(
        required=False,
        allow_blank=True,
        write_only=True,
    )
    product_id = serializers.IntegerField(
        required=False,
        allow_null=True,
        write_only=True,
    )
    source = serializers.ChoiceField(
        choices=Inquiry.Source.choices,
        required=False,
        default=Inquiry.Source.WEBSITE,
    )

    class Meta:
        model = Inquiry
        fields = [
            "name",
            "email",
            "phone",
            "company",
            "product_slug",
            "product_id",
            "source",
            "message",
        ]

    def validate_name(self, value):
        if len(value.strip()) < 2:
            raise serializers.ValidationError("Name must be at least 2 characters.")
        return value.strip()

    def validate_email(self, value):
        return value.strip().lower()

    def validate_phone(self, value):
        cleaned = re.sub(r"[\s\-()]", "", value)
        if not re.match(r"^\+?\d{7,15}$", cleaned):
            raise serializers.ValidationError("Enter a valid phone number.")
        return value.strip()

    def validate_message(self, value):
        if len(value.strip()) < 10:
            raise serializers.ValidationError("Message must be at least 10 characters.")
        return value.strip()

    def validate(self, attrs):
        product_slug = attrs.get("product_slug")
        product_id = attrs.get("product_id")

        if product_slug and product_id:
            raise serializers.ValidationError(
                "Provide either product_slug or product_id, not both."
            )

        product = None
        if product_slug:
            try:
                product = Product.objects.published().get(slug=product_slug)
            except Product.DoesNotExist as exc:
                raise serializers.ValidationError(
                    {"product_slug": "Product not found."}
                ) from exc
        elif product_id:
            try:
                product = Product.objects.published().get(pk=product_id)
            except Product.DoesNotExist as exc:
                raise serializers.ValidationError(
                    {"product_id": "Product not found."}
                ) from exc

        if product and not attrs.get("source"):
            attrs["source"] = Inquiry.Source.PRODUCT_PAGE
        elif not attrs.get("source"):
            attrs["source"] = Inquiry.Source.WEBSITE

        attrs["_product"] = product
        return attrs

    def create(self, validated_data):
        validated_data.pop("product_slug", None)
        validated_data.pop("product_id", None)
        product = validated_data.pop("_product", None)

        inquiry = Inquiry(
            product=product,
            product_name=product.name if product else "",
            **validated_data,
        )
        inquiry.save()
        return inquiry
