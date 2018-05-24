# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from actstream.models import user_stream
from django.conf import settings
from django.views.generic import TemplateView
from django.template.loader import get_template
from django.db.models import Sum

from telepathy.models import Thread
from documents.models import Document
from users.models import User
from users.authBackend import NetidBackend
from catalog.forms import SearchForm


def index(request):
    if request.user.is_authenticated:
        context = {
            'search': SearchForm(),
            'stream': user_stream(request.user).exclude(verb="started following")
        }
        return render(request, "home.html", context)
    else:
        def floor(num, r=1):
            r = 10 ** r
            return int((num // r) * r)

        page_count = Document.objects.all().aggregate(Sum('pages'))['pages__sum']

        context = {
            "login_url": NetidBackend.login_url(""),
            "debug": settings.DEBUG,
            "documents": floor(Document.objects.count()),
            "pages": floor(page_count, 2),
            "users": floor(User.objects.count()),
            "threads": floor(Thread.objects.count()),
        }
        return render(request, "index.html", context)


class HelpView(TemplateView):
    def get_context_data(self):
        r = super(HelpView, self).get_context_data()
        r["faq_md"] = get_template("faq.md").render()
        return r
