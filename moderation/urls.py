from django.urls import path

from . import views

urlpatterns = [
    # --- Main Dashboard ---
    path("", views.moderation_home, name="moderation_home"),
    # --- Logs Publics ---
    path("logs/", views.public_logs, name="public_logs"),
    # --- Representative Request ---
    path(
        "representative-request/",
        views.representative_request,
        name="representative_request",
    ),
    path(
        "representative-request/<int:request_id>/process/",
        views.process_representative_request,
        name="process_representative_request",
    ),
    # --- Moderators Management ---
    path("moderators/", views.moderators_list, name="moderators_list"),
    path("moderators/add/", views.moderator_add, name="moderator_add"),
    path(
        "moderators/remove/<int:user_id>/",
        views.moderator_remove,
        name="moderator_remove",
    ),
    # --- Public Pages ---
    path("tree/", views.moderation_tree, name="moderation_tree"),
    path("about/", views.moderation_about, name="moderation_about"),
]
