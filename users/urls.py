# -*- coding: utf-8 -*-
from __future__ import unicode_literals

# Copyright 2014, Cercle Informatique ASBL. All rights reserved.
#
# This program is free software: you can redistribute it and/or modify it
# under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or (at
# your option) any later version.
#
# This software was made by hast, C4, ititou at UrLab, ULB's hackerspace

from django.conf.urls import patterns, url

urlpatterns = patterns(
    "",

    url(r"^join/(?P<nodeid>\d+)$",
        'users.views.follow_node',
        name="follow_node"),

    url(r"^join_children/(?P<nodeid>\d+)$",
        'users.views.follow_node_children',
        name="follow_node_children"),

    url(r"^leave/(?P<nodeid>\d+)$",
        'users.views.unfollow_node',
        name="unfollow_node"),

    url(r"^settings/$",
        'users.views.user_settings',
        name="settings"),

    url(r"^panel_hide/$",
        'users.views.panel_hide',
        name="hide_new_panel"),
)
