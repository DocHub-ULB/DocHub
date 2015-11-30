# -*- coding: utf-8 -*-
from __future__ import unicode_literals

# Copyright 2014, Cercle Informatique ASBL. All rights reserved.
#
# This program is free software: you can redistribute it and/or modify it
# under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or (at
# your option) any later version.
#
# This software was made by hast, C4, ititou and rom1 at UrLab (http://urlab.be): ULB's hackerspace

from django.conf.urls import patterns, url
import views


def markAsReadAndRedirect(*args, **kwargs):
    kwargs['redirect_to_object'] = True
    return views.markAsRead(*args, **kwargs)

urlpatterns = patterns(
    "",
    url(
        r"^$",
        views.NotificationsView.as_view(),
        name="notifications"
    ),
    url(r"^read/(?P<pk>[0-9]+)$", views.markAsRead, name="mark_as_read"),
    url(r"^redirect/(?P<pk>[0-9]+)$", markAsReadAndRedirect, name="read_and_redirect"),
    url(r"^read_all$", views.markAllAsRead, name="read_all"),
)
