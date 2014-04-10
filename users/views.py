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

from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.core.cache.utils import make_template_fragment_key
from django.core.cache import cache

from polydag.models import Node
from graph.models import Category, Course


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
