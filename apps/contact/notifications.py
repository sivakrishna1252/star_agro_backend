import logging

from django.conf import settings
from django.core.mail import send_mail

logger = logging.getLogger(__name__)


def send_contact_notification(message) -> bool:
    """Email site admins when a visitor submits the contact form."""
    recipient = settings.CONTACT_NOTIFICATION_EMAIL
    if not recipient or not settings.EMAIL_HOST_USER:
        logger.warning("Email not configured; skipping contact notification.")
        return False

    subject = f"[Star Agsurf] Contact: {message.get_subject_display()}"
    body = (
        "New contact form submission\n\n"
        f"Name: {message.name}\n"
        f"Email: {message.email}\n"
        f"Phone: {message.phone or 'N/A'}\n"
        f"Reason: {message.get_subject_display()}\n\n"
        f"Message:\n{message.message}\n\n"
        "---\n"
        f"Submitted at: {message.created_at}\n"
        f"Contact ID: {message.id}\n"
    )

    try:
        send_mail(
            subject=subject,
            message=body,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[recipient],
            fail_silently=False,
        )
        return True
    except Exception:
        logger.exception(
            "Failed to send contact notification email for contact_id=%s",
            message.id,
        )
        return False
