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

from polydag.models import Node
from graph.models import Category, Course


@login_required
def follow_node(request, nodeid):
    node = get_object_or_404(Node, pk=nodeid)
    if isinstance(node, Category):
        for child in node.children(only=[Course]):
            request.user.follow.add(child)
    elif isinstance(node, Course):
        request.user.follow.add(node)
    else:
        raise NotImplementedError("Can not follow a node of type {}".format(node.classBasename()))
    return HttpResponseRedirect(reverse('node_canonic', args=[nodeid]))


@login_required
def unfollow_node(request, nodeid):
    node = get_object_or_404(Node, pk=nodeid)
    if not isinstance(node, Course):
        raise NotImplementedError("Can not unfollow a node of type {}".format(node.classBasename()))
    request.user.follow.remove(node)
    return HttpResponseRedirect(reverse('node_canonic', args=[nodeid]))
