from django.contrib import admin

from .models import ContactMessage


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "phone", "get_reason_display", "status", "created_at")
    list_filter = ("status", "created_at")
    search_fields = ("name", "email", "phone", "subject", "message")
    list_editable = ("status",)
    readonly_fields = ("created_at",)
    date_hierarchy = "created_at"
    fieldsets = (
        (None, {"fields": ("name", "email", "phone", "subject", "message")}),
        ("Management", {"fields": ("status", "created_at")}),
    )

    @admin.display(description="Reason for Contact")
    def get_reason_display(self, obj):
        return obj.get_subject_display()
