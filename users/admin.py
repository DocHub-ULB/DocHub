from django.contrib import admin

from .models import User


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
    filter_horizontal = ("moderated_courses",)

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
                    "moderated_courses",
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
