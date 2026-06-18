from drf_spectacular.utils import extend_schema
from rest_framework.generics import ListAPIView

from apps.categories.models import Category
from api.serializers.categories import CategorySerializer


@extend_schema(tags=["Categories"])
class CategoryListView(ListAPIView):
    serializer_class = CategorySerializer
    queryset = Category.objects.filter(is_active=True)
