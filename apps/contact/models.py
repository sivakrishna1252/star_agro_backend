from django.db import models


class ContactMessage(models.Model):
    class Status(models.TextChoices):
        NEW = "new", "New"
        READ = "read", "Read"
        REPLIED = "replied", "Replied"
        CLOSED = "closed", "Closed"

    class ReasonForContact(models.TextChoices):
        GENERAL_INQUIRY = "general_inquiry", "General Inquiry"
        PRODUCT_INFORMATION = "product_information", "Product Information"
        PRODUCT_SPECIFIC_INQUIRY = "product_specific_inquiry", "Product Specific Inquiry"
        TECHNICAL_SUPPORT = "technical_support", "Technical Support"
        DEALER_INQUIRY = "dealer_inquiry", "Dealer Inquiry"
        DISTRIBUTOR_INQUIRY = "distributor_inquiry", "Distributor Inquiry"
        SAMPLE_REQUEST = "sample_request", "Sample Request"
        PRICING_QUOTATION = "pricing_quotation", "Pricing & Quotation"
        PARTNERSHIP_OPPORTUNITY = "partnership_opportunity", "Partnership Opportunity"
        OTHER = "other", "Other"

    name = models.CharField(max_length=200)
    email = models.EmailField()
    phone = models.CharField(max_length=20, blank=True)
    subject = models.CharField(
        max_length=50,
        choices=ReasonForContact.choices,
        help_text="Reason for contact selected on the website form.",
    )
    message = models.TextField()
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.NEW,
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Contact Message"
        verbose_name_plural = "Contact Messages"

    def __str__(self):
        return f"{self.name} — {self.get_subject_display()}"
