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

from django.conf.urls import patterns, url, include
from django.views.generic import TemplateView
from django.contrib.auth.views import logout
from django.contrib import admin

admin.autodiscover()

import settings


urlpatterns = patterns(
    "",
    # The apps entry points
    url(r"^$", 'www.views.index', name="index"),
    url(r"^p402/$", 'www.views.index', {'p402': True}, name="p402"),
    url(r"^ulb/", include("catalog.urls")),
    url(r"^document/", include("documents.urls")),
    url(r"^telepathy/", include("telepathy.urls")),
    url(r"^users/", include("users.urls")),
    url(r"^notifications/", include("notifications.urls")),

    url(r"^syslogin$", 'django.contrib.auth.views.login', {"template_name": "syslogin.html"}, name="syslogin"),
    url(r"^auth/$", 'users.views.auth'),
    url(r"^logout$", logout, {"next_page": "/"}, name="logout"),

    url(r'^admin/', include(admin.site.urls)),

    url(r'^help/markdown$', TemplateView.as_view(template_name='telepathy/markdown.html'), name="markdown_help"),
    url(r'^help/$', TemplateView.as_view(template_name='help.html'), name="help"),

    url(r'^api/', include("www.rest_urls")),
    url(r'^activity/', include('actstream.urls')),
)

handler400 = 'www.error.error400'
handler403 = 'www.error.error403'
handler404 = 'www.error.error404'
handler500 = 'www.error.error500'


if settings.DEBUG:
    from django.conf.urls.static import static
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
