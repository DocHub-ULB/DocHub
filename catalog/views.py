# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json

from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404, render
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.views.generic.detail import DetailView
from django.views.decorators.cache import cache_page
from mptt.utils import get_cached_trees

from actstream import actions
import actstream

from www.cbv import LoginRequiredMixin
from catalog.models import Category, Course
from catalog.suggestions import suggest


class CategoryDetailView(LoginRequiredMixin, DetailView):
    model = Category
    template_name = "catalog/category.html"
    context_object_name = "category"


class CourseDetailView(LoginRequiredMixin, DetailView):
    model = Course
    template_name = "catalog/course.html"
    context_object_name = "course"

    def get_context_data(self, **kwargs):
        context = super(CourseDetailView, self).get_context_data(**kwargs)
        course = context['course']

        context['documents'] = course.document_set\
            .exclude(state="ERROR", hidden=True)\
            .select_related('user')\
            .prefetch_related('tags')
        context['threads'] = course.thread_set.annotate(Count('message')).order_by('-id')
        context['followers_count'] = len(actstream.models.followers(course))

        return context


@login_required
def join_course(request, slug):
    course = get_object_or_404(Course, slug=slug)
    actions.follow(request.user, course, actor_only=False)
    return HttpResponseRedirect(reverse('course_show', args=[slug]))


@login_required
def leave_course(request, slug):
    course = get_object_or_404(Course, slug=slug)
    actions.unfollow(request.user, course)
    return HttpResponseRedirect(reverse('course_show', args=[slug]))


@login_required
def show_courses(request):
    return render(request, "catalog/my_courses.html", {
        "faculties": Category.objects.get(level=0).children.all(),
        "suggestions": suggest(request.user)
    })


@cache_page(60 * 60)
@login_required
def course_tree(request):
    def course(node):
        return {
            'name': node.name,
            'id': node.id,
            'slug': node.slug,
        }

    def category(node):
        return {
            'name': node.name,
            'id': node.id,
            'children': map(category, node.get_children()),
            'courses': map(course, node.course_set.all()),
        }

    categories = map(category, get_cached_trees(Category.objects.all()))
    return HttpResponse(json.dumps(categories),
                        content_type="application/json")
