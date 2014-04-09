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

import json

from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required

from polydag.models import Node


@login_required
def getNode(req, nodeid, format):
    """
    GET .../<nodeid>
    => {
        'id' : int,
        'name' : str,
        'type' : str,
        'children' : list[{'id':int, 'name':str, 'type':str}, ...],
        ...
    }
    """
    if not format or len(format) == 0:
        format = 'json' if req.is_ajax() else 'html'
    node = get_object_or_404(Node, pk=nodeid)
    return HttpResponse(json.dumps(node.to_dict(True)), content_type="application/json")


@login_required
def list_tags(request, id):
    node = Node.objects.get(id=id)
    keys = [{'id': kw.pk, 'name': kw.name} for kw in node.keywords.all()]
    return HttpResponse(json.dumps(keys), content_type="application/json")
