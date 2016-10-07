# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.detail import DetailView
from django.views.generic.edit import UpdateView
from django.db.models import Count
from reversion.models import Version
from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse

from questions.models import Question, Answer, Vote


class QuestionDetailView(LoginRequiredMixin, DetailView):
    queryset = Question.objects.select_related("course").all()
    template_name = "questions/question.html"
    context_object_name = "question"

    def get_context_data(self, *args, **kwargs):
        context = super(QuestionDetailView, self).get_context_data(*args, **kwargs)
        q = context["question"]

        revision = Version.objects.get_for_object(q).select_related("revision__user").exclude(revision__user=q.user)
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


@login_required
def upvote(request, pk):
    answer = get_object_or_404(Answer, pk=pk)
    if Vote.objects.filter(user=request.user, answer=answer).count() == 0:
        Vote.objects.create(user=request.user, answer=answer)
    return redirect(reverse('question_show', args=(answer.question.pk,)))


@login_required
def downvote(request, pk):
    answer = get_object_or_404(Answer, pk=pk)
    Vote.objects.filter(user=request.user, answer=answer).delete()
    return redirect(reverse('question_show', args=(answer.question.pk,)))


class QuestionUpdateView(LoginRequiredMixin, UpdateView):
    model = Question
    context_object_name = "question"
    fields = ['text', 'context']

    def get_success_url(self):
        return reverse('question_show', args=(self.object.pk,))


class AnswerUpdateView(LoginRequiredMixin, UpdateView):
    model = Answer
    context_object_name = "answer"
    fields = ['text']

    def get_success_url(self):
        return reverse('question_show', args=(self.object.question.pk,))
