from rest_framework import serializers

from apps.products.models import Product


def build_absolute_media_url(request, file_field):
    if not file_field:
        return None
    if request:
        return request.build_absolute_uri(file_field.url)
    return file_field.url


def get_product_card_image(obj, request=None):
    """Thumbnail for listings; falls back to primary gallery image."""
    if obj.thumbnail:
        return build_absolute_media_url(request, obj.thumbnail)
    image = obj.images.filter(is_primary=True).first()
    if not image:
        image = obj.images.first()
    if image:
        return build_absolute_media_url(request, image.image)
    return None
