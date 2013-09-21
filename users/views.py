# Copyright 2012, hast. All rights reserved.
#
# This program is free software: you can redistribute it and/or modify it
# under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or (at
# your option) any later version.

from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect

from polydag.models import Node
from users.models import Profile

def join_node(request, nodeid):
    node = get_object_or_404(Node, pk=nodeid)
    profile = request.user.get_profile()
    profile.follow.add(node)
    return HttpResponseRedirect(reverse('node_canonic',args=[nodeid]))


def leave_node(request, nodeid):
    node = get_object_or_404(Node, pk=nodeid)
    profile = request.user.get_profile()
    profile.follow.remove(node)
    return HttpResponseRedirect(reverse('node_canonic',args=[nodeid]))
