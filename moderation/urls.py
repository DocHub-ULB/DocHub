from django.urls import path

from . import views

urlpatterns = [
    path("", views.moderation_home, name="moderation_home"),
    path(
        "representative-request",
        views.representative_request,
        name="representative_request",
    ),
]
