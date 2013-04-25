# Copyright 2012, hast. All rights reserved.
#
# This program is free software: you can redistribute it and/or modify it
# under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or (at
# your option) any later version.

from django.shortcuts import render
from graph.models import Category, Course
from documents.models import Document
from notify.models import Notification

def home(request):
    explicit_followed = request.user.get_profile().follow.all()
    followed = explicit_followed.instance_of(Course)
    for cat in explicit_followed.instance_of(Category):
        followed |= cat.children().instance_of(Course)

    return render(request, "home.html",
                  {"followed_courses": followed.order_by('Course___slug')})

