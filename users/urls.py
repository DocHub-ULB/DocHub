from django.urls import path
import users.views

urlpatterns = [
    path("settings/", users.views.user_settings, name="settings"),
    path("reset_token/", users.views.reset_token, name="reset_token"),
    path("panel_hide/", users.views.panel_hide, name="hide_new_panel"),
]
