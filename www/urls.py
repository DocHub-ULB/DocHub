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

from django.conf.urls import patterns, url, include
from authentification import app_redirection, ulb_redirection, intranet_auth
from django.contrib.auth.views import login, logout
from django.contrib import admin
admin.autodiscover()

from graph.urls import json_urls as graph_json
from views import home, node_canonic, index
import settings


# decorator whom call function_in if user is authenticated, function_out if not
def user_logged(function_in, function_out):
    def toggle(request, *args, **kwargs):
        if request.user.is_authenticated():
            return function_in(request, *args, **kwargs)
        else:
            return function_out(request, *args, **kwargs)
    return toggle


urlpatterns = patterns("",
    # All JSON urls
    url(r"^json/tree/", include(graph_json)),
    url(r"^json/node/", include("polydag.urls")),

    # The apps entry points
    url(r"^calendar/", include("calendars.urls")),
    url(r"^ulb/", include("graph.urls")),
    url(r"^document/", include("documents.urls")),
    url(r"^telepathy/", include("telepathy.urls")),
    url(r"^notifications/", include("notify.urls")),
    url(r"^users/", include("users.urls")),

    url(r"^node/(?P<nodeid>\d+)$", node_canonic, name="node_canonic"),

    url(r"^$",
        user_logged(home, index),
        name="index"),

    url(r"^syslogin$",
        user_logged(app_redirection, login),
        {"template_name": "syslogin.html"},
        name="syslogin"),

    url(r"^auth/(?P<next_url>.*)$",
        intranet_auth,
        name="auth_entry"),

    url(r"^logout$",
        logout, {"next_page": "/"},
        name="logout"),

    # fragments
    url(r"^", include("fragments.urls")),

    url(r'^admin/', include(admin.site.urls)),
)

if settings.DEBUG:
    from django.conf.urls.static import static
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
