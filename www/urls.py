# Copyright 2012, hast. All rights reserved.
#
# This program is free software: you can redistribute it and/or modify it
# under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or (at
# your option) any later version.

from django.conf.urls import patterns, url, include
from django.views.generic.simple import direct_to_template
from authentification import app_redirection, ulb_redirection, intranet_auth
from django.contrib.auth.views import login, logout
from graph.urls import json_urls as graph_json
from views import home, node_canonic


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
    url(r"^zoidberg/calendar/", include("calendar.urls")),
    url(r"^zoidberg/graph/", include("graph.urls")),
    url(r"^zoidberg/document/", include("documents.urls")),
    url(r"^zoidberg/telepathy/", include("telepathy.urls")),
    url(r"^zoidberg/notifications/", include("notify.urls")),
    url(r"^zoidberg/users/", include("users.urls")),
    
    # The product/client entry points
    url(r"^zoidberg/home$",home,
        name="home"),
    
    url(r"^zoidberg/node/(?P<nodeid>\d+)$", node_canonic, name="node_canonic"),
    
    url(r"^$",
        user_logged(app_redirection, direct_to_template),
        {"template": "index.html"},
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
)
