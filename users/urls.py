# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf.urls import url

urlpatterns = [
    url(r"^settings/$", 'users.views.user_settings', name="settings"),
    url(r"^panel_hide/$", 'users.views.panel_hide', name="hide_new_panel"),
]
