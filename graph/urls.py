# Copyright 2012, hast. All rights reserved.
#
# This program is free software: you can redistribute it and/or modify it
# under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or (at
# your option) any later version.

from django.conf.urls import patterns, url
from graph.views import get_category, show_course, show_category


json_urls = patterns("",
    url(r"^category/(?P<id>[^/]*)$", get_category, name="get_category"),
)


urlpatterns = patterns("",
    url(r"^course/(?P<slug>[^/]*)$", 
        show_course,
        name="course_show"),
    url(r"^cat/(?P<catid>\d+)$", 
        show_category,
        name="category_show"),
)
