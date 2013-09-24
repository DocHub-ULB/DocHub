# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf.urls import patterns, url

urlpatterns = patterns('',
    url(r'^show$', 'notify.views.notifications_show', name="notif_show"),
    url(r'^(?P<id>[^/]*)/read$', 'notify.views.notification_read', name="notif_read")
)