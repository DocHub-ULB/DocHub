from django.contrib import admin

from .models import Inscription, User


class InscriptionInline(admin.TabularInline):
    model = Inscription
    extra = 1


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = (
        "netid",
        "name",
        "is_staff",
        "is_academic",
        "is_representative",
        "last_login",
        "created",
        "inferred_faculty",
        "inscription_faculty",
    )
    list_filter = (
        "is_staff",
        "is_academic",
        "is_representative",
        "last_login",
        "created",
        "inferred_faculty",
        "inscription_faculty",
    )
    search_fields = ("netid", "first_name", "last_name")
    date_hierarchy = "created"

    readonly_fields = (
        "netid",
        "last_login",
        "registration",
        "inferred_faculty",
        "inscription_faculty",
    )
    filter_horizontal = ("moderated_courses",)
    inlines = (InscriptionInline,)

    fieldsets = (
        (
            None,
            {
                "fields": (
                    "netid",
                    "first_name",
                    "last_name",
                    "registration",
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
                    "is_representative",
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


@admin.register(Inscription)
class InscriptionAdmin(admin.ModelAdmin):
    readonly_fields = ("user", "faculty", "section", "year")
    list_display = ("id", "user", "faculty", "section", "year")
    list_filter = (
        "year",
        "faculty",
        "section",
    )
    search_fields = ("section", "user__netid", "user__first_name", "user__last_name")
