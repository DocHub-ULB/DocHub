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
from django.views.generic import TemplateView
from authentification import app_redirection, ulb_redirection, intranet_auth
from django.contrib.auth.views import login, logout
from django.contrib import admin

admin.autodiscover()

from views import home, node_canonic, index, p402
import settings


# decorator whom call function_in if user is authenticated, function_out if not
def user_logged(function_in, function_out):
    def toggle(request, *args, **kwargs):
        if request.user.is_authenticated():
            return function_in(request, *args, **kwargs)
        else:
            return function_out(request, *args, **kwargs)
    return toggle


urlpatterns = patterns(
    "",
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

    url(r"^p402/$", p402, name="p402"),

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

    url(r'^help/markdown$', TemplateView.as_view(template_name='markdown.html'), name="markdown_help"),
    url(r'^help/$', TemplateView.as_view(template_name='help.html'), name="help"),

    url(r'^api/', include("www.rest_urls")),
)

handler400 = 'www.error.error400'
handler403 = 'www.error.error403'
handler404 = 'www.error.error404'
handler500 = 'www.error.error500'


if settings.DEBUG:
    from django.conf.urls.static import static
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
