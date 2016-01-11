# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf.urls import url

import views


urlpatterns = [
    url(r"^$", views.NotificationsView.as_view(), name="notifications"),
    url(r"^read/(?P<pk>[0-9]+)$", views.markAsRead, name="mark_as_read"),
    url(r"^redirect/(?P<pk>[0-9]+)$", views.markAsReadAndRedirect, name="read_and_redirect"),
    url(r"^read_all$", views.markAllAsRead, name="read_all"),
]
