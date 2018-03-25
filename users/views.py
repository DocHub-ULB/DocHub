# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import os
from base64 import b64decode


from PIL import Image, ImageOps
from django.core.urlresolvers import reverse
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponseRedirect, HttpResponseForbidden
from django.contrib.auth import authenticate, login
from django.conf import settings

from actstream.models import actor_stream

from users.forms import SettingsForm


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
    next_url = "/"

    if sid and uid:
        user = authenticate(sid=sid, uid=uid)
        if user is not None:
            user.update_inscription_faculty()
            login(request, user)
            return HttpResponseRedirect(next_url)

    HttpResponseForbidden()
