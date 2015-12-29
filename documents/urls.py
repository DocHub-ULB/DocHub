# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf.urls import url

urlpatterns = [
    url(r"^upload/(?P<slug>[^/]*)$",
        'documents.views.upload_file',
        name="document_put"),

    url(r"^multiple_upload/(?P<slug>[^/]*)$",
        'documents.views.upload_multiple_files',
        name="document_put_multiple"),

    url(r"^(?P<pk>[^/]*)/edit$",
        'documents.views.document_edit',
        name="document_edit"),

    url(r"^(?P<pk>[^/]*)/download$",
        'documents.views.document_download',
        name="document_download"),

    url(r"^(?P<pk>[^/]*)/original$",
        'documents.views.document_download_original',
        name="document_download_original"),

    url(r"^(?P<pk>[^/]*)$",
        'documents.views.document_show',
        name="document_show"),
]
