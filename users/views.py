# -*- coding: utf-8 -*-
from __future__ import unicode_literals

# Copyright 2012, hast. All rights reserved.
#
# This program is free software: you can redistribute it and/or modify it
# under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or (at
# your option) any later version.

from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required

from polydag.models import Node


@login_required
def follow_node(request, nodeid):
    node = get_object_or_404(Node, pk=nodeid)
    request.user.follow.add(node)
    return HttpResponseRedirect(reverse('node_canonic', args=[nodeid]))


@login_required
def unfollow_node(request, nodeid):
    node = get_object_or_404(Node, pk=nodeid)
    request.user.follow.remove(node)
    return HttpResponseRedirect(reverse('node_canonic', args=[nodeid]))
