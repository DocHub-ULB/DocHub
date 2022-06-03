from django.urls import path

import users.views

urlpatterns = [
    path("panel_hide/", users.views.panel_hide, name="hide_new_panel"),
]
