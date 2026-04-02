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
        "target_item",
        "target_field",
        "old_value",
        "new_value",
        "timestamp",
    )
    list_filter = ("target_field", "timestamp", "content_type")
    search_fields = ("user__netid", "object_id", "old_value", "new_value")

    @admin.display(description="Objet ciblé")
    def target_item(self, obj):
        """Retourne le nom lisible de l'objet ciblé au lieu de son simple numéro d'ID"""
        if obj.content_object:
            return str(obj.content_object)
        return f"ID {obj.object_id} (Supprimé)"
