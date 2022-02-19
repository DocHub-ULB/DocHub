from django.urls import path

import users.views

urlpatterns = [
    path("reset_token/", users.views.reset_token, name="reset_token"),
    path("panel_hide/", users.views.panel_hide, name="hide_new_panel"),
    path(
        "add_moderated_course/",
        users.views.add_moderated_course,
        name="add_moderated_course",
    ),
]
