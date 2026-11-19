from django.urls import path

import users.views

urlpatterns = [
    path("tokens/", users.views.api_tokens, name="api_tokens"),
    path(
        "tokens/<int:pk>/delete",
        users.views.api_token_delete,
        name="api_token_delete",
    ),
    path("panel_hide/", users.views.panel_hide, name="hide_new_panel"),
    path(
        "moderator_banner_hide/",
        users.views.moderator_banner_hide,
        name="moderator_banner_hide",
    ),
]
