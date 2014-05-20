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
from graph.views import get_category, show_course, show_category, show_courses


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

    url(r"^courses/$",
        show_courses,
        name="show_courses"),
)
