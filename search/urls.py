# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.urls import path

from . import views

urlpatterns = [
    path("courses/", views.CourseSearchView.as_view(), name="course_search"),
]
