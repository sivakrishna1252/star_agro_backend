from django.contrib import admin

from .models import Inquiry, InquiryNote


class InquiryNoteInline(admin.TabularInline):
    model = InquiryNote
    extra = 1
    fields = ("note", "created_by", "created_at")
    readonly_fields = ("created_by", "created_at")


@admin.register(Inquiry)
class InquiryAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "email",
        "phone",
        "company",
        "product_name",
        "source",
        "status",
        "created_at",
    )
    list_filter = ("status", "source", "product", "created_at")
    search_fields = ("name", "email", "phone", "company", "product_name", "message")
    list_editable = ("status",)
    readonly_fields = ("product_name", "created_at", "updated_at")
    autocomplete_fields = ("product",)
    date_hierarchy = "created_at"
    inlines = [InquiryNoteInline]
    fieldsets = (
        (
            "Lead Information",
            {
                "fields": (
                    "name",
                    "email",
                    "phone",
                    "company",
                    "product",
                    "product_name",
                    "source",
                    "message",
                )
            },
        ),
        (
            "Management",
            {"fields": ("status", "admin_notes", "created_at", "updated_at")},
        ),
    )

    actions = ["mark_as_contacted", "mark_as_qualified", "mark_as_closed"]

    @admin.action(description="Mark selected as Contacted")
    def mark_as_contacted(self, request, queryset):
        queryset.update(status=Inquiry.Status.CONTACTED)

    @admin.action(description="Mark selected as Qualified")
    def mark_as_qualified(self, request, queryset):
        queryset.update(status=Inquiry.Status.QUALIFIED)

    @admin.action(description="Mark selected as Closed")
    def mark_as_closed(self, request, queryset):
        queryset.update(status=Inquiry.Status.CLOSED)

    def save_formset(self, request, form, formset, change):
        instances = formset.save(commit=False)
        for instance in instances:
            if isinstance(instance, InquiryNote) and not instance.pk:
                instance.created_by = request.user
            instance.save()
        formset.save_m2m()


@admin.register(InquiryNote)
class InquiryNoteAdmin(admin.ModelAdmin):
    list_display = ("inquiry", "note_preview", "created_by", "created_at")
    list_filter = ("created_at",)
    search_fields = ("inquiry__name", "note")
    autocomplete_fields = ("inquiry",)
    readonly_fields = ("created_by", "created_at")

    @admin.display(description="Note")
    def note_preview(self, obj):
        return obj.note[:80] + "..." if len(obj.note) > 80 else obj.note

    def save_model(self, request, obj, form, change):
        if not change:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)
