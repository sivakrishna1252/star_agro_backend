from drf_spectacular.utils import OpenApiExample, OpenApiParameter, extend_schema
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from api.serializers.contact import ContactMessageCreateSerializer
from api.serializers.inquiries import InquiryCreateSerializer


class InquiryCreateView(APIView):
    @extend_schema(
        tags=["Forms"],
        summary="Submit product inquiry",
        description="Submit a B2B product or distributor inquiry. Link a product via `product_slug` or `product_id`.",
        request=InquiryCreateSerializer,
        responses={
            201: {
                "type": "object",
                "properties": {
                    "success": {"type": "boolean"},
                    "message": {"type": "string"},
                    "inquiry_id": {"type": "integer"},
                    "product_id": {"type": "integer", "nullable": True},
                    "product_name": {"type": "string"},
                },
            },
            400: {"description": "Validation error"},
        },
        examples=[
            OpenApiExample(
                "Product inquiry",
                value={
                    "name": "John Doe",
                    "email": "john@example.com",
                    "phone": "+919876543210",
                    "company": "Agri Distributors Ltd",
                    "product_slug": "stagsurf-sc-6875",
                    "source": "product_page",
                    "message": "Interested in bulk supply for EC formulations.",
                },
                request_only=True,
            ),
        ],
    )
    def post(self, request):
        serializer = InquiryCreateSerializer(data=request.data)
        if serializer.is_valid():
            inquiry = serializer.save()
            return Response(
                {
                    "success": True,
                    "message": "Your inquiry has been submitted successfully.",
                    "inquiry_id": inquiry.id,
                    "product_id": inquiry.product_id,
                    "product_name": inquiry.product_name,
                },
                status=status.HTTP_201_CREATED,
            )
        return Response(
            {"success": False, "errors": serializer.errors},
            status=status.HTTP_400_BAD_REQUEST,
        )
