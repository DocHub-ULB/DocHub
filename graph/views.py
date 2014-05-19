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
import itertools

from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404, render
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.core.cache import cache

from documents.forms import UploadFileForm
from telepathy.forms import NewThreadForm
from graph.models import Category, Course
from telepathy.models import Thread
from documents.models import Document
from calendars.gehol import gehol_url
from polydag.models import Keyword
from www.helpers import year_choices


@login_required
def get_category(request, id):
    category = get_object_or_404(Category, id=id)
    jsoniser = lambda category: {
        "id": category.id,
        "name": category.name,
        "description": category.description,
        "contains": [
            {
                "id": c.id,
                "name": c.name,
                "slug": c.slug
            } for c in category.children().instance_of(Category, Course)]
    }

    return HttpResponse(dumps(jsoniser(category)), mimetype='application/json')


@login_required
def show_category(request, catid):
    cat = get_object_or_404(Category, pk=catid)

    children = set(cat.children(only=[Course]))
    followed_nodes = set(request.user.directly_followed())

    follow_children = not children <= followed_nodes

    followed = cat in followed_nodes

    return render(request, "category.html", {
        'object': cat,
        'follow_children': follow_children,
        'followed': followed,
    })


@login_required
def show_course(request, slug):
    if re.search(r'^\d+$', slug):
        course = get_object_or_404(Course, pk=slug)
        return HttpResponseRedirect(reverse('course_show', args=[course.slug]))
    else:
        course = get_object_or_404(Course, slug=slug)

    children = course.children().non_polymorphic()
    docs = filter(lambda x: x.get_real_instance_class() == Document, children)
    docs = map(lambda x: x.id, docs)
    docs = Document.objects.filter(id__in=docs).select_related('user').prefetch_related('keywords')

    threads = filter(lambda x: x.get_real_instance_class() == Thread, children)
    threads = map(lambda x: x.id, threads)
    threads = Thread.objects.filter(id__in=threads).annotate(Count('message')).select_related('user').prefetch_related('keywords')
    children_nodes = itertools.chain(docs, threads)

    get_date = lambda x: getattr(x, "date", False) or getattr(x, "created", False)
    sorted_children_nodes = []
    year_dict = {}
    for node in children_nodes:
        l = year_dict.get(node.year, [])
        l.append(node)
        year_dict[node.year] = l

    for year, _ in year_choices():
        elements = year_dict.pop(year, [])
        elements = reversed(sorted(elements, key=get_date))
        sorted_children_nodes += elements

    for unknown_year in year_dict.keys():
        nodes = year_dict.pop(unknown_year)
        for node in nodes:
            node.year = "Archives"
        sorted_children_nodes += nodes

    followed = request.user.follows(course)

    tags = cache.get('all_tags')
    if tags is None:
        tags = list(map(lambda x: x.name, Keyword.objects.all()))
        cache.set('all_tags', ",".join(tags), 300)
    else:
        tags = tags.split(",")


    return render(request, "course.html", {
        "object": course,
        "gehol": gehol_url(course),
        "followed": followed,
        "tags": tags,
        'children_nodes': sorted_children_nodes,
    })


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
