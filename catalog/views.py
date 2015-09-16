# -*- coding: utf-8 -*-
from __future__ import unicode_literals

# Copyright 2014, Cercle Informatique ASBL. All rights reserved.
#
# This program is free software: you can redistribute it and/or modify it
# under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or (at
# your option) any later version.
#
# This software was made by hast, C4, ititou at UrLab, ULB's hackerspace

from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404, render
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.db.models import Count

from actstream import actions
import actstream

from catalog.models import Category, Course
from tags.models import Tag


@login_required
def show_category(request, catid):
    category = get_object_or_404(Category, pk=catid)

    return render(request, "catalog/category.html", {
        'category': category,
    })


@login_required
def show_course(request, slug):
    course = get_object_or_404(Course, slug=slug)

    docs = course.document_set.exclude(state="ERROR").order_by('-id')
    threads = course.thread_set.annotate(Count('message')).order_by('-id')

    return render(request, "catalog/course.html", {
        "course": course,
        "documents": docs.filter(hidden=False).select_related('user').prefetch_related('tags'),
        "threads": threads,
        "followers_count": len(actstream.models.followers(course)),
        "all_tags": Tag.objects.all(),
    })


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
        "faculties": Category.objects.get(level=0).children.all()
    })
