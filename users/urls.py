from django.urls import path

import users.views

urlpatterns = [
    path("panel_hide/", users.views.panel_hide, name="hide_new_panel"),
    path(
        "moderator_banner_hide/",
        users.views.moderator_banner_hide,
        name="moderator_banner_hide",
    ),
]
