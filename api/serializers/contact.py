import re

from rest_framework import serializers

from apps.contact.models import ContactMessage


def _reason_label_map():
    return {choice.label.lower(): choice.value for choice in ContactMessage.ReasonForContact}


class ContactReasonSerializer(serializers.Serializer):
    value = serializers.CharField()
    label = serializers.CharField()


class ContactMessageCreateSerializer(serializers.ModelSerializer):
    reason = serializers.ChoiceField(
        choices=ContactMessage.ReasonForContact.choices,
        write_only=True,
        required=False,
    )
    subject = serializers.ChoiceField(
        choices=ContactMessage.ReasonForContact.choices,
        required=False,
    )

    class Meta:
        model = ContactMessage
        fields = ["name", "email", "phone", "reason", "subject", "message"]

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

    def validate_message(self, value):
        if len(value.strip()) < 10:
            raise serializers.ValidationError("Message must be at least 10 characters.")
        return value.strip()

    def _normalize_reason(self, value):
        if value in ContactMessage.ReasonForContact.values:
            return value

        label_match = _reason_label_map().get(str(value).strip().lower())
        if label_match:
            return label_match

        raise serializers.ValidationError(
            "Select a valid reason for contact."
        )

    def validate_reason(self, value):
        return self._normalize_reason(value)

    def validate_subject(self, value):
        return self._normalize_reason(value)

    def _resolve_reason(self, attrs):
        reason = attrs.pop("reason", None)
        subject = attrs.get("subject")

        if reason and subject and reason != subject:
            raise serializers.ValidationError(
                {"reason": "Provide either reason or subject, not both with different values."}
            )

        resolved = reason or subject
        if not resolved:
            raise serializers.ValidationError(
                {"reason": "Reason for contact is required."}
            )

        attrs["subject"] = resolved
        return attrs

    def validate(self, attrs):
        return self._resolve_reason(attrs)
