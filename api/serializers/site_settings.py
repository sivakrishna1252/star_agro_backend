from rest_framework import serializers

from apps.site_settings.models import SiteSettings


class SiteSettingsSerializer(serializers.ModelSerializer):
    company_logo_url = serializers.SerializerMethodField()

    class Meta:
        model = SiteSettings
        fields = [
            "site_name",
            "company_logo_url",
            "tagline",
            "about_us",
            "vision",
            "mission",
            "manufacturing_expertise",
            "rd_focus",
            "sustainability",
            "client_commitment",
            "contact_email",
            "contact_phone",
            "contact_address",
            "whatsapp_number",
            "facebook_url",
            "linkedin_url",
            "instagram_url",
            "twitter_url",
            "youtube_url",
            "updated_at",
        ]

    def get_company_logo_url(self, obj):
        if not obj.company_logo:
            return None
        request = self.context.get("request")
        if request:
            return request.build_absolute_uri(obj.company_logo.url)
        return obj.company_logo.url
