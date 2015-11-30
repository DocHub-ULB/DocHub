# -*- coding: utf-8 -*-
from __future__ import unicode_literals

# Copyright 2014, Cercle Informatique ASBL. All rights reserved.
#
# This program is free software: you can redistribute it and/or modify it
# under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or (at
# your option) any later version.
#
# This software was made by hast, C4, ititou and rom1 at UrLab (http://urlab.be): ULB's hackerspace

from django.conf.urls import patterns, url

urlpatterns = patterns(
    "",

    url(r"^course/(?P<slug>[^/]*)$",
        'catalog.views.show_course',
        name="course_show"),

    url(r"^cat/(?P<catid>\d+)$",
        'catalog.views.show_category',
        name="category_show"),

    url(r"^courses/$",
        'catalog.views.show_courses',
        name="show_courses"),

    url(r"^join/(?P<slug>[^/]*)$",
        'catalog.views.join_course',
        name="join_course"),

    url(r"^leave/(?P<slug>[^/]*)$",
        'catalog.views.leave_course',
        name="leave_course"),
)
