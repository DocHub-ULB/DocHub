# Copyright 2012, hast. All rights reserved.
#
# This program is free software: you can redistribute it and/or modify it
# under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or (at
# your option) any later version.

from django.views.generic.list_detail import object_detail
from django.conf.urls import patterns, url
from documents.views import upload_file, document_show
from documents.models import Document


urlpatterns = patterns("",
    url(r"^put/$",
        upload_file,
        name="document_put"),

    url(r"^v/(?P<id>[^/]*)$",
        document_show,
        name="document_show"),
)
