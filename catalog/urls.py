# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf.urls import url
from catalog.views import CategoryDetailView, CourseDetailView
import catalog.views

urlpatterns = [
    url(r"^course/(?P<slug>[\w-]+)$", CourseDetailView.as_view(), name="course_show"),
    url(r"^category/(?P<pk>\d+)$", CategoryDetailView.as_view(), name="category_show"),

    url(r"^join/(?P<slug>[\w-]+)$", catalog.views.join_course, name="join_course"),
    url(r"^leave/(?P<slug>[\w-]+)$", catalog.views.leave_course, name="leave_course"),
    url(r"^subscribed_courses/$", catalog.views.show_courses, name="show_courses"),
    url(r"^unfollow_all_courses/$", catalog.views.unfollow_all_courses, name="unfollow_all_courses"),

    url(r"^course_tree.json$", catalog.views.course_tree, name="course_tree"),
]
