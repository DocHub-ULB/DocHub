from django.urls import path

from . import views

urlpatterns = [
    # --- Public Landing ---
    path("", views.moderation_about, name="moderation_about"),
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
    path("manage/", views.manage_moderators, name="manage_moderators"),
    path("manage/add/", views.moderator_add, name="moderator_add"),
    path(
        "manage/remove/<int:user_id>/",
        views.moderator_remove,
        name="moderator_remove",
    ),
    # --- Public Pages ---
    path("tree/", views.moderation_tree, name="moderation_tree"),
    path("profile/<str:netid>/", views.moderation_profile, name="moderation_profile"),
    # --- Document History ---
    path(
        "document/<int:pk>/history/",
        views.document_history,
        name="document_history",
    ),
]
