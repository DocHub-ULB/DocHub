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
from telepathy.views import new_thread, show_thread, show_thread_fragment, reply_thread, edit_message


urlpatterns = patterns("",
    url(r"^put/(?P<parent_id>[^/]*)$",
        new_thread,
        name="thread_put"),

    url(r"^reply/(?P<thread_id>[^/]*)$",
        reply_thread,
        name="thread_reply"),

    url(r"^v/(?P<thread_id>[^/]*)/$",
        show_thread,
        name="thread_show"),

    url(r"^fragment/(?P<thread_id>[^/]*)/$",
        show_thread_fragment,
        name="thread_show_fragment"),

    url(r"^edit/(?P<message_id>[^/]*)$",
        edit_message,
        name="edit_message"),
)
