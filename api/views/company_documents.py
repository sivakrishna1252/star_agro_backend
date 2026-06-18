from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework.generics import ListAPIView

from apps.documents.models import CompanyDocument
from api.serializers.company_documents import CompanyDocumentSerializer


@extend_schema(
    tags=["Documents"],
    parameters=[
        OpenApiParameter(
            name="type",
            description="COMPANY_PROFILE, COMPANY_BROCHURE, CERTIFICATE, TECHNICAL_CATALOG, OTHER",
            type=str,
        ),
    ],
)
class CompanyDocumentListView(ListAPIView):
    serializer_class = CompanyDocumentSerializer

    def get_queryset(self):
        queryset = CompanyDocument.objects.filter(is_active=True)

        document_type = self.request.query_params.get("type")
        if document_type:
            queryset = queryset.filter(document_type=document_type.upper())

        return queryset
