from rest_framework import serializers

from apps.documents.models import ProductDocument


class DocumentSerializer(serializers.ModelSerializer):
    file_url = serializers.SerializerMethodField()
    product_name = serializers.CharField(source="product.name", read_only=True)
    product_slug = serializers.CharField(source="product.slug", read_only=True)

    class Meta:
        model = ProductDocument
        fields = [
            "id",
            "document_name",
            "document_type",
            "file_url",
            "product_name",
            "product_slug",
            "display_order",
            "created_at",
        ]

    def get_file_url(self, obj):
        request = self.context.get("request")
        if request:
            return request.build_absolute_uri(obj.file.url)
        return obj.file.url
