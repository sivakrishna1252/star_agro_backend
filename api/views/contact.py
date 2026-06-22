from drf_spectacular.utils import OpenApiExample, extend_schema
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from api.serializers.contact import ContactMessageCreateSerializer, ContactReasonSerializer
from apps.contact.models import ContactMessage
from apps.contact.notifications import send_contact_notification


class ContactReasonListView(APIView):
    @extend_schema(
        tags=["Forms"],
        summary="List contact form reason options",
        description=(
            "Returns the dropdown options for the contact page "
            "'Reason for Contact' field."
        ),
        responses={200: ContactReasonSerializer(many=True)},
    )
    def get(self, request):
        reasons = [
            {"value": choice.value, "label": choice.label}
            for choice in ContactMessage.ReasonForContact
        ]
        return Response(reasons)


class ContactCreateView(APIView):
    @extend_schema(
        tags=["Forms"],
        summary="Submit general contact message",
        description="Submit a general contact message (not tied to a specific product).",
        request=ContactMessageCreateSerializer,
        responses={
            201: {
                "type": "object",
                "properties": {
                    "success": {"type": "boolean"},
                    "message": {"type": "string"},
                    "contact_id": {"type": "integer"},
                },
            },
            400: {"description": "Validation error"},
        },
        examples=[
            OpenApiExample(
                "Contact message",
                value={
                    "name": "Jane Smith",
                    "email": "jane@company.com",
                    "phone": "+919876543210",
                    "reason": "partnership_opportunity",
                    "message": "We would like to discuss distribution partnership.",
                },
                request_only=True,
            ),
        ],
    )
    def post(self, request):
        serializer = ContactMessageCreateSerializer(data=request.data)
        if serializer.is_valid():
            message = serializer.save()
            send_contact_notification(message)
            return Response(
                {
                    "success": True,
                    "message": "Your message has been sent successfully.",
                    "contact_id": message.id,
                },
                status=status.HTTP_201_CREATED,
            )
        return Response(
            {"success": False, "errors": serializer.errors},
            status=status.HTTP_400_BAD_REQUEST,
        )
