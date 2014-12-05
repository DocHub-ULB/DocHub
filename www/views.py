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

import urllib

from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required

from graph.models import Category, Course
from telepathy.models import Thread
from polydag.models import Node
from documents.models import Document
from notify.models import PreNotification
from users.models import Inscription
from .helpers import current_year

import settings

Mapping = {
    Course: 'course_show',
    Thread: 'thread_show',
    Document: 'document_show',
    Category: 'category_show'
}


@login_required
def node_canonic(request, nodeid):
    n = get_object_or_404(Node, pk=nodeid)
    for klass in Mapping:
        action = Mapping[klass]
        if type(n) == klass:
            return HttpResponseRedirect(reverse(action, args=[n.id]))


def index(request):
    next_url = request.GET.get("next", False)
    if next_url:
        next_url = urllib.quote_plus("next=" + next_url.strip() + "&")
        next_url = urllib.quote_plus(next_url)

        ulb_url = settings.ULB_LOGIN + next_url
    else:
        ulb_url = settings.ULB_LOGIN
    return render(request, "index.html", {"login_url": ulb_url, "debug": settings.DEBUG})


@login_required
def home(request):
    followed = request.user.directly_followed()
    ids = map(lambda x: x.id, followed)
    for node in followed:
        ids += map(lambda x: x.id, node.children())
    wall = PreNotification.objects.filter(node__in=ids).filter(personal=False).order_by('-created').select_related('user')[:20]

    welcome = {}
    if request.user.welcome:
        inscription = Inscription.objects.filter(user=request.user).order_by('-year').first()
        if inscription and inscription.year == current_year():
            welcome['inscription'] = inscription
        elif inscription and inscription.year == current_year() - 1:
            welcome['inscription'] = inscription
            welcome['new_inscriptions'] = [inscription] + list(inscription.next)

    return render(request, "home.html",
                  {"wall": wall,
                   "welcome": welcome,
                   })
