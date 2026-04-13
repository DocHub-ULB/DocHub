from django.urls import path

from . import views

urlpatterns = [
    path("", views.moderation_home, name="moderation_home"),
    path(
        "representative-request",
        views.representative_request,
        name="representative_request",
    ),
    # New architecture for moderator management
    path("moderators/", views.moderators_list, name="moderators_list"),
    path("moderators/add/", views.moderator_add, name="moderator_add"),
    path(
        "moderators/remove/<int:user_id>/",
        views.moderator_remove,
        name="moderator_remove",
    ),
    path(
        "process-request/<int:request_id>/",
        views.process_representative_request,
        name="process_representative_request",
    ),
]
