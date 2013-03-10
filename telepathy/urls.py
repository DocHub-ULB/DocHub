# Copyright 2012, hast. All rights reserved.
#
# This program is free software: you can redistribute it and/or modify it
# under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or (at
# your option) any later version.

from django.conf.urls import patterns, url
from telepathy.views import new_thread, show_thread


urlpatterns = patterns("",
    url(r"^put/", 
        new_thread,
        name="thread_put"),

    url(r"^v/(?P<thread_id>[^/]*)/$", 
        show_thread,
        name="thread_show"),
)
