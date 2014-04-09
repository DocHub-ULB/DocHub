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

from json import dumps
import re

from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404, render
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.decorators import login_required

from documents.forms import UploadFileForm
from telepathy.forms import NewThreadForm
from graph.models import Category, Course
from telepathy.models import Thread
from documents.models import Document
from calendars.gehol import gehol_url
from polydag.models import to_django


@login_required
def get_category(request, id):
    category = get_object_or_404(Category, id=id)
    jsoniser = lambda category: {
        "id": category.id,
        "name": category.name,
        "description": category.description,
        "contains": [
            {"id": c.id,
             "name": c.name,
             "slug": c.slug
             } for c in category.children().instance_of(Category, Course)]
    }

    return HttpResponse(dumps(jsoniser(category)), mimetype='application/json')


@login_required
def show_category(request, catid):
    cat = get_object_or_404(Category, pk=catid)
    children = to_django(cat.children())
    cat.course_set = children.instance_of(Course)
    cat.subcategory_set = children.instance_of(Category)
    followed = cat in request.user.directly_followed()
    return render(request, "category.html", {'object': cat, 'followed': followed})


@login_required
def show_course(request, slug):
    if re.search(r'^\d+$', slug):
        course = get_object_or_404(Course, pk=slug)
    else:
        course = get_object_or_404(Course, slug=slug)
    children = to_django(course.children())
    course.thread_set = children.instance_of(Thread)
    course.document_set = children.instance_of(Document)
    followed = course in request.user.directly_followed()
    return render(request, "course.html",
                  {"object": course,
                   "gehol": gehol_url(course),
                   "upload_form": UploadFileForm(initial={"course": course}),
                   "followed": followed,
                   "newthread_form": NewThreadForm(initial={"parentNode": course.id})})


@login_required
def join_course(request, slug):
    course = get_object_or_404(Course, slug=slug)
    user = request.user
    user.follow.add(course)
    return HttpResponseRedirect(reverse('course_show', args=[slug]))


@login_required
def leave_course(request, slug):
    course = get_object_or_404(Course, slug=slug)
    user = request.user
    user.follow.remove(course)
    return HttpResponseRedirect(reverse('course_show', args=[slug]))
