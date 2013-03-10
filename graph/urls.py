# Copyright 2012, hast. All rights reserved.
#
# This program is free software: you can redistribute it and/or modify it
# under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or (at
# your option) any later version.

from django.conf.urls import patterns, url
from graph.views import get_category, show_course, join_course, leave_course


json_urls = patterns("",
    url(r"^category/(?P<id>[^/]*)$", get_category, name="get_category"),
)


urlpatterns = patterns("",
    url(r"^v/(?P<slug>[^/]*)$", 
        show_course,
        name="course_show"),
    
    url(r"^join/(?P<slug>[^/]*)$", 
        join_course,
        name="course_join"),

    url(r"^leave/(?P<slug>[^/]*)$", 
        leave_course,
        name="course_leave"),
)
