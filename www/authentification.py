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

from django.http import HttpResponseRedirect, HttpResponseForbidden
from django.shortcuts import render
from django.core.urlresolvers import reverse
from django.contrib.auth import authenticate, login


def intranet_auth(request, next_url):
    sid, uid = request.GET.get("_sid", False), request.GET.get("_uid", False)
    if len(next_url.strip()) == 0:
        next_url = request.GET.get("next", reverse("index")).strip()
    if sid and uid:
        user = authenticate(sid=sid, uid=uid)
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(next_url)
        else:
            HttpResponseForbidden()
    else:
        return render(request, 'error.html', {'msg': 'url discarded'})
