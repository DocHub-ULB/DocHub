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

from django.utils.html import escape
from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404, render
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.decorators import login_required

from documents.models import Document, Page
from graph.models import Course
from polydag.models import Node
from documents.forms import UploadFileForm
from www import settings


@login_required
def upload_file(request, parent_id):
    parentNode = get_object_or_404(Node, id=parent_id)
    if not isinstance(parentNode, Course):
        raise NotImplementedError("Not a course")

    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)

        if form.is_valid():
            if len(form.cleaned_data['name']) > 0:
                name = form.cleaned_data['name']
            else:
                name, _ = os.path.splitext(request.FILES['file'].name)
                name = name.lower()

            extension = os.path.splitext(request.FILES['file'].name)[1][1:].lower()
            description = form.cleaned_data['description']
            course = parentNode

            doc = Document.objects.create(user=request.user,
                                          name=name, description=description, state="pending")
            course.add_child(doc)

            if not os.path.exists(settings.TMP_UPLOAD_DIR):
                os.makedirs(settings.TMP_UPLOAD_DIR)

            tmp_file = os.path.join(settings.TMP_UPLOAD_DIR, "{}.{}".format(doc.id, extension))
            source = 'file://' + tmp_file
            doc.source = source

            doc.save() # Save document after copy to avoid corrupted state if copy failed

            return HttpResponseRedirect(reverse('course_show', args=[course.slug]))

    else:
        form = UploadFileForm()

    return render(request, 'document_upload.html', {
        'form': form,
        'parent': parentNode,
    })


@login_required
def document_download(request, id):
    doc = get_object_or_404(Document, id=id)
    with open(doc.pdf) as fd:
        body = fd.read()
    response = HttpResponse(body, content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="%s.pdf"' % (doc.name)
    doc.downloads += 1
    doc.save()
    return response


@login_required
def document_download_original(request, id):
    doc = get_object_or_404(Document, id=id)
    with open(doc.staticfile) as fd:
        body = fd.read()
    response = HttpResponse(body, content_type='application/octet-stream')
    response['Content-Description'] = 'File Transfer'
    response['Content-Transfer-Encoding'] = 'binary'
    response['Content-Disposition'] = 'attachment; filename="{}.{}"'.format(doc.name, doc.original_extension())
    doc.downloads += 1
    doc.save()
    return response


@login_required
def document_show(request, id):
    document = get_object_or_404(Document, id=id)

    children = document.children()
    document.page_set = children.instance_of(Page)

    context = {
        "object": document,
        "parent": document.parent,
        "is_moderator": request.user.is_moderator(document.parent)
    }
    document.views += 1
    document.save()
    return render(request, "viewer.html", context)
