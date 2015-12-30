# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf.urls import url, include
from django.views.generic import TemplateView
from django.contrib.auth.views import logout, login
from django.contrib import admin
from django.conf import settings

from www.legacy_urls import urlpatterns as legacy_patterns


urlpatterns = [
    url(r"^$", 'www.views.index', name="index"),
    url(r"^catalog/", include("catalog.urls")),
    url(r"^documents/", include("documents.urls")),
    url(r"^telepathy/", include("telepathy.urls")),
    url(r"^users/", include("users.urls")),
    url(r"^notifications/", include("notifications.urls")),

    url(r"^syslogin$", login, {"template_name": "syslogin.html"}, name="syslogin"),
    url(r"^auth/$", 'users.views.auth'),
    url(r"^logout$", logout, {"next_page": "/"}, name="logout"),

    url(r'^admin/', include(admin.site.urls)),

    url(r'^help/markdown$', TemplateView.as_view(template_name='telepathy/markdown.html'), name="markdown_help"),
    url(r'^help/$', TemplateView.as_view(template_name='help.html'), name="help"),

    url(r'^api/', include("www.rest_urls")),

] + legacy_patterns

handler400 = 'www.error.error400'
handler403 = 'www.error.error403'
handler404 = 'www.error.error404'
handler500 = 'www.error.error500'


if settings.DEBUG:
    from django.conf.urls.static import static
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
