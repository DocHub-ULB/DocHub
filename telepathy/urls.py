# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf.urls import url
import telepathy.views

urlpatterns = [
    url(r"^put/(?P<course_slug>[\w-]+)$", telepathy.views.new_thread, name="thread_put"),
    url(r"^doc_put/(?P<document_id>\d+)$", telepathy.views.new_thread, name="document_thread_put"),
    url(r"^(?P<pk>\d+)/reply$", telepathy.views.reply_thread, name="thread_reply"),
    url(r"^(?P<pk>\d+)/$", telepathy.views.show_thread, name="thread_show"),
    url(r"^fragment/(?P<pk>\d+)/$", telepathy.views.show_thread_fragment, name="thread_show_fragment"),
    url(r"^(?P<pk>\d+)/edit$", telepathy.views.edit_message, name="edit_message"),
    url(r"^join/(?P<pk>\d+)$", telepathy.views.join_thread, name="join_thread"),
    url(r"^leave/(?P<pk>\d+)$", telepathy.views.leave_thread, name="leave_thread"),
]
