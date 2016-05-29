# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf.urls import url
import questions.views

urlpatterns = [
    url(r"^(?P<pk>[^/]*)/$", questions.views.CategoryDetailView.as_view(), name="question_show"),
]
