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

import os
from PIL import Image, ImageOps

from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404, render
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.core.cache.utils import make_template_fragment_key
from django.core.cache import cache
from django.contrib import messages

from polydag.models import Node
from graph.models import Category, Course
from www import settings

from forms import SettingsForm


def empty_user_followed_list_cache(user):
    cache.delete(make_template_fragment_key('user_followed_list', [user.netid]))


@login_required
def follow_node(request, nodeid):
    node = get_object_or_404(Node, pk=nodeid)
    request.user.follow.add(node)
    empty_user_followed_list_cache(request.user)
    return HttpResponseRedirect(reverse('node_canonic', args=[nodeid]))


@login_required
def follow_node_children(request, nodeid):
    node = get_object_or_404(Node, pk=nodeid)
    for child in node.children(only=[Course]):
        request.user.follow.add(child)
    empty_user_followed_list_cache(request.user)
    return HttpResponseRedirect(reverse('node_canonic', args=[nodeid]))


@login_required
def unfollow_node(request, nodeid):
    node = get_object_or_404(Node, pk=nodeid)
    request.user.follow.remove(node)
    empty_user_followed_list_cache(request.user)
    return HttpResponseRedirect(reverse('node_canonic', args=[nodeid]))


@login_required
def user_settings(request):
    if request.method == 'POST':
        form = SettingsForm(request.POST, request.FILES)

        if form.is_valid():
            im = Image.open(request.FILES['profile_pic'])
            im = ImageOps.fit(im, (120, 120), Image.ANTIALIAS)
            im.save(os.path.join(settings.MEDIA_ROOT, "profile/{}.png".format(request.user.netid)))
            request.user.photo = "png"
            request.user.save()
            messages.success(request, 'Votre profil a été mis à jour.')
            return render(request, "settings.html", {'form': SettingsForm()})

    else:
        form = SettingsForm()

    return render(request, 'settings.html', {
        'form': form,
    })


@login_required
def panel_hide(request):
    request.user.welcome = False
    request.user.save()

    return HttpResponseRedirect(reverse('index'))
