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

urlpatterns = patterns('',
    url(r'^show$', 'notify.views.notifications_show', name="notif_show"),
    url(r'^read_all$', 'notify.views.notification_read_all', name="notif_read_all"),
    url(r'^(?P<id>[^/]*)/read$', 'notify.views.notification_read', name="notif_read"),
    url(r'^(?P<id>[^/]*)/ajax_read$', 'notify.views.notification_ajax_read', name="notif_ajax_read")
)