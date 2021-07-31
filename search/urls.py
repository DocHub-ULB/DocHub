# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf.urls import url

from . import views

urlpatterns = [
    url(r"^courses/$", views.CourseSearchView.as_view(), name="course_search"),
]
