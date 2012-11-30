# Copyright 2012, hast. All rights reserved.
#
# This program is free software: you can redistribute it and/or modify it
# under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or (at
# your option) any later version.

from django.views.generic.list_detail import object_detail
from django.conf.urls import patterns, url
from documents.forms import UploadFileForm
from graph.views import get_category, join_course, leave_course
from graph.models import Course


json_urls = patterns("",
    url(r"^category/(?P<id>[^/]*)$", get_category, name="get_category"),
)


urlpatterns = patterns("",
    url(r"^v/(?P<slug>[^/]*)$", 
        object_detail,
        {"slug_field": "slug",
         "template_name": "course.html",
         "queryset": Course.objects.all(),
         "extra_context": {"upload_form": UploadFileForm()}},
        name="course_show"),
    
    url(r"^join/(?P<slug>[^/]*)$", 
        join_course,
        name="course_join"),

    url(r"^leave/(?P<slug>[^/]*)$", 
        leave_course,
        name="course_leave"),
)
