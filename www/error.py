# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render


def error400(request):
    return render(request, "error/400.html", status=400)


def error403(request):
    return render(request, "error/403.html", status=403)


def error404(request):
    return render(request, "error/404.html", status=404)


def error500(request):
    return render(request, "error/500.html", status=500)
