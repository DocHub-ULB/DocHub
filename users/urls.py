from django.urls import path

import users.views

urlpatterns = [
    path(
        "moderator_banner_hide/",
        users.views.moderator_banner_hide,
        name="moderator_banner_hide",
    ),
]
