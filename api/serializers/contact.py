import re

from rest_framework import serializers

from apps.contact.models import ContactMessage


class ContactMessageCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactMessage
        fields = ["name", "email", "phone", "subject", "message"]

    def validate_name(self, value):
        if len(value.strip()) < 2:
            raise serializers.ValidationError("Name must be at least 2 characters.")
        return value.strip()

    def validate_email(self, value):
        return value.strip().lower()

    def validate_phone(self, value):
        if not value:
            return ""
        cleaned = re.sub(r"[\s\-()]", "", value)
        if not re.match(r"^\+?\d{7,15}$", cleaned):
            raise serializers.ValidationError("Enter a valid phone number.")
        return value.strip()

    def validate_subject(self, value):
        if len(value.strip()) < 3:
            raise serializers.ValidationError("Subject must be at least 3 characters.")
        return value.strip()

    def validate_message(self, value):
        if len(value.strip()) < 10:
            raise serializers.ValidationError("Message must be at least 10 characters.")
        return value.strip()
