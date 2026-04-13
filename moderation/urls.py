from django.urls import path

from . import views

urlpatterns = [
    path("", views.moderation_home, name="moderation_home"),
    path(
        "representative-request",
        views.representative_request,
        name="representative_request",
    ),
    path(
        "manage-moderators/", views.moderators_management, name="moderators_management"
    ),
    path(
        "process-request/<int:request_id>/",
        views.process_representative_request,
        name="process_representative_request",
    ),
]
