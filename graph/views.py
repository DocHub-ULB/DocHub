# Copyright 2012, hast. All rights reserved.
#
# This program is free software: you can redistribute it and/or modify it
# under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or (at
# your option) any later version.

from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404, render
from django.http import HttpResponse, HttpResponseRedirect
from documents.forms import UploadFileForm
from telepathy.forms import NewThreadForm
from graph.models import Category, Course
from json import dumps


def get_category(request, id):
    category = get_object_or_404(Category, id=id)
    jsoniser = lambda category: {
        "id": category.id,
         "name": category.name,
         "description": category.description,
         "sub_categories": [{"name": sc.name,
                             "description": sc.description,
                             "id": sc.id} for sc in category.sub_categories.all()],
         "contains": [{"id": cours.id,
                       "name": cours.name,
                       "description": cours.description,
                       "slug": cours.slug} for cours in category.contains.all()]}

    return HttpResponse(dumps(jsoniser(category)), mimetype='application/json')


def show_course(request, slug):
    course = get_object_or_404(Course, slug=slug)
    return render(request, "course.html", 
                  {"object": course,
                   "upload_form": UploadFileForm(initial={"course": course}),
                   "newthread_form": NewThreadForm(initial={
                        "referer_type": "course",
                        "referer_id": course.id})})


def join_course(request, slug):
    course = get_object_or_404(Course, slug=slug)
    user = request.user.get_profile()
    user.follow.add(course)
    return HttpResponseRedirect(reverse('course_show', args=[slug]))

def leave_course(request, slug):
    course = get_object_or_404(Course, slug=slug)
    user = request.user.get_profile()
    user.follow.remove(course)
    return HttpResponseRedirect(reverse('course_show', args=[slug]))
