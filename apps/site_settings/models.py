from django.db import models
from ckeditor.fields import RichTextField


class SiteSettings(models.Model):
    """Singleton model for website content and contact information."""

    site_name = models.CharField(max_length=255, blank=True, default="")
    company_logo = models.ImageField(upload_to="site/", blank=True, null=True)
    tagline = models.CharField(max_length=500, blank=True)
    about_us = RichTextField(blank=True)
    vision = RichTextField(blank=True)
    mission = RichTextField(blank=True)
    manufacturing_expertise = models.TextField(blank=True)
    rd_focus = models.TextField(blank=True, verbose_name="R&D Focus")
    sustainability = models.TextField(blank=True)
    client_commitment = models.TextField(blank=True)
    contact_email = models.EmailField(blank=True)
    contact_phone = models.CharField(max_length=30, blank=True)
    contact_address = models.TextField(blank=True)
    whatsapp_number = models.CharField(max_length=30, blank=True)
    facebook_url = models.URLField(blank=True)
    linkedin_url = models.URLField(blank=True)
    instagram_url = models.URLField(blank=True)
    twitter_url = models.URLField(blank=True)
    youtube_url = models.URLField(blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Site Settings"
        verbose_name_plural = "Site Settings"

    def __str__(self):
        return self.site_name or "Site Settings"

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    @classmethod
    def load(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj

    def delete(self, *args, **kwargs):
        pass
