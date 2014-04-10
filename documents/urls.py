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
from documents.views import upload_file, document_show, document_download
from documents.models import Document


urlpatterns = patterns("",
    url(r"^put/(?P<parent_id>[^/]*)$",
        upload_file,
        name="document_put"),

    url(r"^dl/(?P<id>[^/]*)$",
        document_download,
        name="document_download"),

    url(r"^v/(?P<id>[^/]*)$",
        document_show,
        name="document_show"),
)
