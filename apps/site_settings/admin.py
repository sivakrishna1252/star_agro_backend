from django.contrib import admin

from .models import SiteSettings


@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    fieldsets = (
        (
            "Branding",
            {"fields": ("site_name", "company_logo", "tagline")},
        ),
        (
            "About Us",
            {
                "fields": (
                    "about_us",
                    "vision",
                    "mission",
                    "manufacturing_expertise",
                    "rd_focus",
                    "sustainability",
                    "client_commitment",
                )
            },
        ),
        (
            "Contact Information",
            {
                "fields": (
                    "contact_email",
                    "contact_phone",
                    "contact_address",
                    "whatsapp_number",
                )
            },
        ),
        (
            "Social Media Links",
            {
                "fields": (
                    "facebook_url",
                    "linkedin_url",
                    "instagram_url",
                    "twitter_url",
                    "youtube_url",
                ),
                "classes": ("collapse",),
            },
        ),
    )

    def has_add_permission(self, request):
        return not SiteSettings.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False
