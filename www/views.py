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

from django.shortcuts import render
from django.core.cache import cache

from telepathy.models import Thread
from documents.models import Document, Page
from notify.models import PreNotification
from users.models import User
from users.authBackend import NetidBackend

import settings


def index(request, p402=False):
    if not request.user.is_authenticated():
        context = auth_page_context(request)
        if p402:
            return render(request, "p402.html", context)
        else:
            return render(request, "index.html", context)
    else:
        return feed(request)


def auth_page_context(request):
    next_url = request.GET.get("next", "")

    def floor(num, r=1):
        r = 10 ** r
        return int((num // r) * r)

    return {
        "login_url": NetidBackend.login_url(next_url),
        "debug": settings.DEBUG,
        "documents": floor(Document.objects.count()),
        "pages": floor(Page.objects.count(), 2),
        "users": floor(User.objects.count()),
        "threads": floor(Thread.objects.count()),
    }


def feed(request):
    followed_ids = cache.get('user.wall.followed_nodes.' + str(request.user.id))
    if followed_ids is None:
        followed = request.user.directly_followed()
        ids = map(lambda x: x.id, list(followed))
        for node in followed:
            ids += map(lambda x: x.id, node.children())

        followed_ids = ids
        cache.set('user.wall.followed_nodes.' + str(request.user.id), followed_ids, 300)

    wall = PreNotification.objects.filter(node__in=followed_ids)
    wall = wall.filter(personal=False).order_by('-created')
    wall = wall.select_related('user')[:20]

    return render(request, "home.html", {"wall": wall})
