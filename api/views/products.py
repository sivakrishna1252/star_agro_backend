from django.db.models import Prefetch, Q
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import status
from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.products.models import Product, ProductImage
from api.serializers.products import ProductDetailSerializer, ProductListSerializer
from api.serializers.search import search_products

PRODUCT_FILTER_PARAMS = [
    OpenApiParameter(name="category", description="Filter by category slug", type=str),
    OpenApiParameter(name="formulation_type", description="Filter by formulation type", type=str),
    OpenApiParameter(name="formulation", description="Alias for formulation_type", type=str),
    OpenApiParameter(name="product_type", description="Formulation type or category slug", type=str),
    OpenApiParameter(name="featured", description="Set to true for featured only", type=str),
]


class ProductFilterMixin:
    """Shared filtering logic for product list and search endpoints."""

    def apply_product_filters(self, queryset):
        params = self.request.query_params

        category = params.get("category")
        if category:
            queryset = queryset.filter(category__slug=category)

        formulation_type = params.get("formulation_type") or params.get("formulation")
        if formulation_type:
            queryset = queryset.filter(formulation_type__iexact=formulation_type)

        product_type = params.get("product_type")
        if product_type:
            queryset = queryset.filter(
                Q(formulation_type__iexact=product_type) | Q(category__slug=product_type)
            )

        featured = params.get("featured")
        if featured is not None and featured.lower() in ("true", "1", "yes"):
            queryset = queryset.filter(is_featured=True)

        return queryset.order_by("display_order", "name")


@extend_schema(tags=["Products"], parameters=PRODUCT_FILTER_PARAMS)
class ProductListView(ProductFilterMixin, ListAPIView):
    serializer_class = ProductListSerializer

    def get_queryset(self):
        queryset = Product.objects.published().select_related("category")
        queryset = queryset.prefetch_related(
            Prefetch(
                "images",
                queryset=ProductImage.objects.order_by("-is_primary", "display_order"),
            )
        )
        return self.apply_product_filters(queryset)


@extend_schema(tags=["Products"])
class ProductDetailView(RetrieveAPIView):
    serializer_class = ProductDetailSerializer
    lookup_field = "slug"

    def get_queryset(self):
        return (
            Product.objects.published()
            .select_related("category")
            .prefetch_related(
                "images",
                "properties",
                "benefits",
                "applications",
                "documents",
            )
        )


@extend_schema(tags=["Products"])
class FeaturedProductListView(ListAPIView):
    serializer_class = ProductListSerializer

    def get_queryset(self):
        return (
            Product.objects.published()
            .filter(is_featured=True)
            .select_related("category")
            .prefetch_related("images")
            .order_by("display_order", "name")
        )


class ProductSearchView(ProductFilterMixin, APIView):
    @extend_schema(
        tags=["Products"],
        summary="Search published products",
        parameters=[
            OpenApiParameter(name="q", description="Search query (min 2 chars)", required=True, type=str),
            *PRODUCT_FILTER_PARAMS,
        ],
        responses={200: ProductListSerializer(many=True)},
    )
    def get(self, request):
        query = request.query_params.get("q", "").strip()
        if len(query) < 2:
            return Response(
                {"detail": "Search query must be at least 2 characters."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        queryset = search_products(query)
        queryset = self.apply_product_filters(queryset)

        serializer = ProductListSerializer(
            queryset, many=True, context={"request": request}
        )
        return Response(
            {
                "query": query,
                "count": len(serializer.data),
                "results": serializer.data,
            }
        )
