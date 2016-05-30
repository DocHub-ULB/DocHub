# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.detail import DetailView
from django.db.models import Count
from reversion import revisions

from questions.models import Question, Answer

class CategoryDetailView(LoginRequiredMixin, DetailView):
    queryset = Question.objects.select_related("course").all()
    template_name = "questions/question.html"
    context_object_name = "question"

    def get_context_data(self, *args, **kwargs):
        context = super(CategoryDetailView, self).get_context_data(*args, **kwargs)
        q = context["question"]

        revision = revisions.get_for_object(q).select_related("revision__user").exclude(revision__user=q.user)
        authors = set(map(lambda x: x.revision.user, revision))

        context["answers"] = q\
            .answer_set.annotate(Count('votes'))\
            .prefetch_related("votes", "votes__user")\
            .order_by("-votes__count")
        for answer in context["answers"]:
            if self.request.user in list(map(lambda x: x.user, answer.votes.all())):
                answer.has_voted = True
            else:
                answer.has_voted = False
        context["authors"] = authors
        return context
