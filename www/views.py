# Copyright 2012, hast. All rights reserved.
#
# This program is free software: you can redistribute it and/or modify it
# under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or (at
# your option) any later version.

from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.core.urlresolvers import reverse
from graph.models import Category, Course
from telepathy.models import Thread
from polydag.models import Node
from documents.models import Document
import settings

Mapping = {
    Course : 'course_show',
    Thread : 'thread_show',
    Document : 'document_show',
    Category : 'category_show'
}
def node_canonic(request, nodeid):
    n = get_object_or_404(Node, pk=nodeid)
    for klass in Mapping:
        action = Mapping[klass]
        if type(n) == klass:
            return HttpResponseRedirect(reverse(action, args=[n.id]))

def index(request):
    return render(request, "index.html", {"login_url": settings.ULB_LOGIN})

def home(request):
    explicit_followed = request.user.get_profile().follow.all()
    followed = explicit_followed.instance_of(Course)
    for cat in explicit_followed.instance_of(Category):
        followed |= cat.children().instance_of(Course)

    return render(request, "home.html",
                  {"followed_courses": followed.order_by('Course___slug')})

