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
    return render(request, "index.html", {"login_url": settings.ULB_LOGIN, "debug": settings.DEBUG})


@login_required
def home(request):
    followed_ids = request.user.followed_nodes_id()
    wall = PreNotification.objects.filter(node__in=followed_ids).filter(personal=False).order_by('-created')

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
