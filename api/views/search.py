from django.db.models import Q
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import serializers
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.categories.models import Category
from api.serializers.categories import CategorySerializer
from api.serializers.products import ProductListSerializer
from api.serializers.search import search_products


class GlobalSearchResultSerializer(serializers.Serializer):
    type = serializers.CharField()
    id = serializers.IntegerField()
    name = serializers.CharField()
    slug = serializers.CharField()


class SearchView(APIView):
    @extend_schema(
        tags=["Search"],
        summary="Global search (products + categories)",
        parameters=[
            OpenApiParameter(name="q", description="Search query (min 2 chars)", required=True, type=str),
        ],
        responses={200: GlobalSearchResultSerializer(many=True)},
    )
    def get(self, request):
        query = request.query_params.get("q", "").strip()
        if len(query) < 2:
            return Response(
                {"detail": "Search query must be at least 2 characters."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        products = search_products(query)[:20]
        product_data = ProductListSerializer(
            products, many=True, context={"request": request}
        ).data

        categories = Category.objects.filter(is_active=True).filter(
            Q(name__icontains=query) | Q(description__icontains=query)
        )[:10]
        category_data = CategorySerializer(
            categories, many=True, context={"request": request}
        ).data

        results = [
            *[{"type": "product", **item} for item in product_data],
            *[
                {
                    "type": "category",
                    "id": c["id"],
                    "name": c["name"],
                    "slug": c["slug"],
                    "description": (c.get("description") or "")[:200],
                }
                for c in category_data
            ],
        ]

        return Response({"query": query, "count": len(results), "results": results})
