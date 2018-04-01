# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json
from functools import partial

from django.urls import reverse
from django.shortcuts import get_object_or_404, render, redirect
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count
from django.views.generic.detail import DetailView
from django.views.decorators.cache import cache_page
from mptt.utils import get_cached_trees
from django.utils import timezone

from actstream import actions
import actstream

from catalog.models import Category, Course
from catalog.suggestions import suggest


class CategoryDetailView(LoginRequiredMixin, DetailView):
    model = Category
    template_name = "catalog/category.html"
    context_object_name = "category"


class CourseDetailView(DetailView):
    model = Course
    context_object_name = "course"

    def get_template_names(self, **kwargs):
        if self.request.user.is_authenticated():
            return "catalog/course.html"
        else:
            return "catalog/noauth/course.html"

    def get_context_data(self, **kwargs):
        context = super(CourseDetailView, self).get_context_data(**kwargs)
        course = context['course']

        context['documents'] = course.document_set\
            .exclude(state="ERROR", hidden=True)\
            .select_related('user')\
            .prefetch_related('tags')
        context['threads'] = course.thread_set.annotate(Count('message')).order_by('-id')
        context['followers_count'] = course.followers_count

        return context


def set_follow_course(request, slug, action):
    course = get_object_or_404(Course, slug=slug)
    action(request.user, course)
    request.user.update_inferred_faculty()
    nextpage = request.GET.get('next', reverse('course_show', args=[slug]))
    return HttpResponseRedirect(nextpage)


@login_required
def join_course(request, slug):
    follow = partial(actions.follow, actor_only=False)
    return set_follow_course(request, slug, follow)


@login_required
def leave_course(request, slug):
    return set_follow_course(request, slug, actions.unfollow)


@login_required
def show_courses(request):
    end_of_year = timezone.now().month in [7, 8, 9, 10]
    return render(request, "catalog/my_courses.html", {
        "faculties": Category.objects.get(level=0).children.all(),
        "suggestions": suggest(request.user),
        "show_unfollow_all_button": end_of_year
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
            'children': list(map(category, node.get_children())),
            'courses': list(map(course, node.course_set.all())),
        }

    categories = list(map(category, get_cached_trees(Category.objects.prefetch_related('course_set').all())))
    return HttpResponse(json.dumps(categories),
                        content_type="application/json")


@login_required
def unfollow_all_courses(request):
    for course in request.user.following_courses():
        actions.unfollow(request.user, course)
    return redirect("show_courses")
