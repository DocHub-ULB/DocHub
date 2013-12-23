# -*- coding: utf-8 -*-
from __future__ import unicode_literals

# Copyright 2012, hast. All rights reserved.
#
# This program is free software: you can redistribute it and/or modify it
# under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or (at
# your option) any later version.

from django.conf.urls import patterns, url
from users.views import follow_node, unfollow_node

urlpatterns = patterns("",
    url(r"^join/(?P<nodeid>\d+)$",
        follow_node,
        name="follow_node"),

    url(r"^leave/(?P<nodeid>\d+)$",
        unfollow_node,
        name="unfollow_node"),
)
