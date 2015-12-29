# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf.urls import url

urlpatterns = [
    url(r"^course/(?P<slug>[^/]*)$", 'catalog.views.show_course', name="course_show"),
    url(r"^category/(?P<catid>\d+)$", 'catalog.views.show_category', name="category_show"),

    url(r"^join/(?P<slug>[^/]*)$", 'catalog.views.join_course', name="join_course"),
    url(r"^leave/(?P<slug>[^/]*)$", 'catalog.views.leave_course', name="leave_course"),
    url(r"^subscribed_courses/$", 'catalog.views.show_courses', name="show_courses"),
]
