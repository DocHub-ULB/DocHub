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

urlpatterns = patterns(
    "",

    url(r"^put/(?P<course_slug>[^/]*)$",
        'telepathy.views.new_thread',
        name="thread_put"),

    url(r"^doc_put/(?P<document_id>[^/]*)$",
        'telepathy.views.new_thread',
        name="document_thread_put"),

    url(r"^reply/(?P<thread_id>[^/]*)$",
        'telepathy.views.reply_thread',
        name="thread_reply"),

    url(r"^v/(?P<thread_id>[^/]*)/$",
        'telepathy.views.show_thread',
        name="thread_show"),

    url(r"^fragment/(?P<thread_id>[^/]*)/$",
        'telepathy.views.show_thread_fragment',
        name="thread_show_fragment"),

    url(r"^edit/(?P<message_id>[^/]*)$",
        'telepathy.views.edit_message',
        name="edit_message"),

    url(r"^join/(?P<id>[^/]*)$",
        'telepathy.views.join_thread',
        name="join_thread"),

    url(r"^leave/(?P<id>[^/]*)$",
        'telepathy.views.leave_thread',
        name="leave_thread"),
)
