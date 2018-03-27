# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf.urls import url
import users.views

urlpatterns = [
    url(r"^settings/$", users.views.user_settings, name="settings"),
    url(r"^reset_token/$", users.views.reset_token, name="reset_token"),
    url(r"^panel_hide/$", users.views.panel_hide, name="hide_new_panel"),
]
