from django.contrib import admin

from moderation.models import ModerationLog, RepresentativeRequest


@admin.register(RepresentativeRequest)
class RepresentativeRequestAdmin(admin.ModelAdmin):
    list_display = ("user", "faculty", "processed", "created")
    list_filter = ("processed",)


@admin.register(ModerationLog)
class ModerationLogAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "content_type",
        "object_id",
        "target_field",
        "old_value",
        "new_value",
        "timestamp",
    )
    list_filter = ("target_field", "timestamp", "content_type")
    search_fields = ("user__netid", "object_id", "old_value", "new_value")
