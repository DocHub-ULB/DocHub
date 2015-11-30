# -*- coding: utf-8 -*-
from __future__ import unicode_literals

# Copyright 2014, Cercle Informatique ASBL. All rights reserved.
#
# This program is free software: you can redistribute it and/or modify it
# under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or (at
# your option) any later version.
#
# This software was made by hast, C4, ititou and rom1 at UrLab (http://urlab.be): ULB's hackerspace

import os
from PIL import Image, ImageOps
from base64 import b64decode


from django.core.urlresolvers import reverse
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponseRedirect, HttpResponseForbidden
from django.contrib.auth import authenticate, login

from actstream.models import actor_stream

from www import settings

from forms import SettingsForm


@login_required
def user_settings(request):
    if request.method == 'POST':
        form = SettingsForm(request.POST, request.FILES)

        if form.is_valid():
            im = Image.open(request.FILES['profile_pic'])
            im = ImageOps.fit(im, (120, 120), Image.ANTIALIAS)

            if not os.path.exists(os.path.join(settings.MEDIA_ROOT, "profile")):
                os.makedirs(os.path.join(settings.MEDIA_ROOT, "profile"))

            im.save(os.path.join(settings.MEDIA_ROOT, "profile/{}.png".format(request.user.netid)))
            request.user.photo = "png"
            request.user.save()

            messages.success(request, 'Votre profil a été mis à jour.')

            return render(request, "users/settings.html", {'form': SettingsForm()})
    else:
        form = SettingsForm()

    return render(request, 'users/settings.html', {
        'form': form,
        'stream': actor_stream(request.user),
    })


@login_required
def panel_hide(request):
    request.user.welcome = False
    request.user.save()

    return HttpResponseRedirect(reverse('index'))


def auth(request):
    sid, uid = request.GET.get("_sid", False), request.GET.get("_uid", False)
    next_url = request.GET.get("next", "")
    if next_url != "":
        next_url = b64decode(next_url)
    else:
        next_url = "/"

    if sid and uid:
        user = authenticate(sid=sid, uid=uid)
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(next_url)

    HttpResponseForbidden()
