from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework.generics import ListAPIView

from apps.documents.models import ProductDocument
from api.serializers.documents import DocumentSerializer


@extend_schema(
    tags=["Documents"],
    parameters=[
        OpenApiParameter(name="type", description="Document type: TDS, BROCHURE, CATALOG, MSDS, PRODUCT_SHEET", type=str),
        OpenApiParameter(name="product", description="Filter by product slug", type=str),
    ],
)
class DocumentListView(ListAPIView):
    serializer_class = DocumentSerializer

    def get_queryset(self):
        queryset = ProductDocument.objects.filter(is_active=True).select_related("product")

        document_type = self.request.query_params.get("type")
        if document_type:
            queryset = queryset.filter(document_type=document_type.upper())

        product_slug = self.request.query_params.get("product")
        if product_slug:
            queryset = queryset.filter(product__slug=product_slug)

        return queryset
