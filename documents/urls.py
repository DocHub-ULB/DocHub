# Copyright 2012, hast. All rights reserved.
#
# This program is free software: you can redistribute it and/or modify it
# under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or (at
# your option) any later version.

from django.views.generic.list_detail import object_detail
from django.conf.urls import patterns, url
from documents.views import upload_file, show_document
from documents.models import Document


urlpatterns = patterns("",
    url(r"^put/$", 
        upload_file,
        name="document_put"),

    url(r"^v/(?P<doc_id>[^/]*)$",
        show_document,
        name='document_show')
    
    #url(r"^v/(?P<object_id>[^/]*)$", 
    #    object_detail,
    #    {"template_name": "viewer.html",
    #     "queryset": Document.objects.all()},
    #    name="document_show"),
)
