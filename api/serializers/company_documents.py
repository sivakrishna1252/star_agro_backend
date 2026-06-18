from rest_framework import serializers

from apps.documents.models import CompanyDocument


class CompanyDocumentSerializer(serializers.ModelSerializer):
    file_url = serializers.SerializerMethodField()

    class Meta:
        model = CompanyDocument
        fields = [
            "id",
            "title",
            "document_type",
            "file_url",
            "display_order",
            "created_at",
        ]

    def get_file_url(self, obj):
        request = self.context.get("request")
        if request:
            return request.build_absolute_uri(obj.pdf_file.url)
        return obj.pdf_file.url
