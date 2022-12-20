from django.contrib import admin

from moderation.models import RepresentativeRequest


@admin.register(RepresentativeRequest)
class RepresentativeRequestAdmin(admin.ModelAdmin):
    list_display = ("user", "faculty", "processed", "created")
    list_filter = ("processed",)
