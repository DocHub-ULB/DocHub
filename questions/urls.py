# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf.urls import url
import questions.views

urlpatterns = [
    url(r"^add/$", questions.views.QuestionDetailView.as_view(), name="question_add"),
    url(r"^(?P<pk>[^/]*)/$", questions.views.QuestionDetailView.as_view(), name="question_show"),
    url(r"^(?P<pk>[^/]*)/respond$", questions.views.QuestionDetailView.as_view(), name="question_respond"),
    url(r"^(?P<pk>[^/]*)/edit$", questions.views.QuestionUpdateView.as_view(), name="question_edit"),

    url(r"^answer/(?P<pk>[^/]*)/edit$", questions.views.AnswerUpdateView.as_view(), name="question_answer_edit"),
    url(r"^answer/(?P<pk>[^/]*)/upvote$", questions.views.upvote, name="question_answer_upvote"),
    url(r"^answer/(?P<pk>[^/]*)/downvote$", questions.views.downvote, name="question_answer_downvote"),
]
