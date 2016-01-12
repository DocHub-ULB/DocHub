# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf.urls import url
from django.views.generic.base import RedirectView


class DocumentRedirectView(RedirectView):
    permanent = False
    query_string = True
    pattern_name = 'document_show'

urlpatterns = [
    url(r'^document/v/(?P<pk>[^/]*)$', DocumentRedirectView.as_view()),
    url(r'^p402$', RedirectView.as_view(url='/', permanent=True))
]
