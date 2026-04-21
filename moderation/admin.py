from django.contrib import admin

from moderation.models import ModerationLog, RepresentativeRequest


@admin.register(RepresentativeRequest)
class RepresentativeRequestAdmin(admin.ModelAdmin):
    list_display = ("user", "faculty", "role", "processed", "created")
    list_filter = ("processed", "faculty", "role")
    search_fields = ("user__netid", "user__email")


@admin.register(ModerationLog)
class ModerationLogAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "timestamp",
        "display_action",
        "display_target",
        "display_details",
    )
    list_filter = ("target_field", "timestamp", "content_type")
    search_fields = ("user__netid", "object_id")

    def get_queryset(self, request):
        """Hide old technical logs to keep the admin clean"""
        qs = super().get_queryset(request)
        return qs.exclude(target_field__in=["processed", "rejection_reason", "statut"])

    @admin.display(description="Action")
    def display_action(self, obj):
        return obj.action_text

    @admin.display(description="Cible")
    def display_target(self, obj):
        return obj.target_text

    @admin.display(description="Détails")
    def display_details(self, obj):
        return obj.details_text
