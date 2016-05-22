# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from actstream.models import user_stream
from django.conf import settings

from telepathy.models import Thread
from documents.models import Document, Page
from users.models import User
from users.authBackend import NetidBackend


def index(request):
    if request.user.is_authenticated():
        context = {
            'stream': user_stream(request.user).exclude(verb="started following")
        }
        return render(request, "home.html", context)
    else:
        def floor(num, r=1):
            r = 10 ** r
            return int((num // r) * r)

        context = {
            "login_url": NetidBackend.login_url(""),
            "debug": settings.DEBUG,
            "documents": floor(Document.objects.count()),
            "pages": floor(Page.objects.count(), 2),
            "users": floor(User.objects.count()),
            "threads": floor(Thread.objects.count()),
        }
        return render(request, "index.html", context)
