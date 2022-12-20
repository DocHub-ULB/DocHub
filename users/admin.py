from django.contrib import admin

from .models import User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = (
        "netid",
        "name",
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
    search_fields = ("netid", "first_name", "last_name")
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
                    "last_login",
                )
            },
        ),
        (
            "Notifications",
            {
                "classes": ("collapse",),
                "fields": (
                    "notify_on_response",
                    "notify_on_new_doc",
                    "notify_on_new_thread",
                ),
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
