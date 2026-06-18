from drf_spectacular.utils import extend_schema
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.site_settings.models import SiteSettings
from api.serializers.site_settings import SiteSettingsSerializer


@extend_schema(
    tags=["CMS"],
    summary="Get site settings and CMS content",
    responses={200: SiteSettingsSerializer},
)
class SiteSettingsView(APIView):
    def get(self, request):
        settings = SiteSettings.load()
        serializer = SiteSettingsSerializer(settings)
        return Response(serializer.data)
