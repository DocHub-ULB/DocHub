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

urlpatterns = patterns(
    "",

    url(r"^course/(?P<slug>[^/]*)$",
        'graph.views.show_course',
        name="course_show"),
    url(r"^cat/(?P<catid>\d+)$",
        'graph.views.show_category',
        name="category_show"),

    url(r"^courses/$",
        'graph.views.show_courses',
        name="show_courses"),
)
