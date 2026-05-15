from django.contrib import admin

from .models import CasFailure, User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = (
        "netid",
        "name",
        "email",
        "is_staff",
        "is_academic",
        "is_moderator",
        "last_login",
        "created",
    )
    list_filter = (
        "is_staff",
        "is_academic",
        "is_moderator",
        "last_login",
        "created",
    )
    search_fields = ("netid", "first_name", "last_name", "email")
    date_hierarchy = "created"

    readonly_fields = (
        "netid",
        "last_login",
    )
    fieldsets = (
        (
            None,
            {
                "fields": (
                    "netid",
                    "first_name",
                    "last_name",
                    "email",
                    "last_login",
                )
            },
        ),
        (
            "Moderation",
            {
                "classes": ("collapse",),
                "fields": (
                    "is_staff",
                    "is_academic",
                    "is_moderator",
                ),
            },
        ),
        (
            "Other",
            {
                "classes": ("collapse",),
                "fields": (
                    "welcome",
                    "comment",
                ),
            },
        ),
    )


@admin.register(CasFailure)
class CasFailureAdmin(admin.ModelAdmin):
    list_display = ("code", "ticket", "ip_address", "created")
    list_filter = ("code",)
    search_fields = ("ticket", "details", "ip_address")
    date_hierarchy = "created"
    readonly_fields = ("code", "details", "ticket", "ip_address", "created")

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False
