# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf.urls import patterns, url

urlpatterns = patterns('',
    url(r'^show$', 'notify.views.notifications_show', name="notif_show"),
    url(r'^read_all$', 'notify.views.notification_read_all', name="notif_read_all"),
    url(r'^(?P<id>[^/]*)/read$', 'notify.views.notification_read', name="notif_read"),
    url(r'^(?P<id>[^/]*)/ajax_read$', 'notify.views.notification_ajax_read', name="notif_ajax_read")
)