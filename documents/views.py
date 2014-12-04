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
import uuid
import shutil

from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404, render
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.db.models import F

from documents.models import Document, Page
from graph.models import Course
from polydag.models import Node
from documents.forms import UploadFileForm, FileForm
from www import settings

from cycle import add_document_to_queue


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

            if not os.path.exists(settings.TMP_UPLOAD_DIR):
                os.makedirs(settings.TMP_UPLOAD_DIR)

            tmp_file = os.path.join(settings.TMP_UPLOAD_DIR, str(uuid.uuid4()))
            with open(tmp_file, "w") as f:
                f.write(request.FILES['file'].read())

            doc = Document.objects.create(user=request.user,
                                          name=name, description=description, state="PREPARING")
            course.add_child(doc)

            doc.add_keywords(*form.cleaned_data['tags'])
            doc.year = form.cleaned_data['year']

            if os.path.exists(doc._default_folder()):
                raise Exception("Directory already used (doc {}): '{}'".format(doc.id, doc._default_folder()))

            os.makedirs(doc._default_folder())
            shutil.move(tmp_file, doc._default_original_path(extension))

            doc.original = doc._default_original_path(extension)
            doc.state = 'READY_TO_QUEUE'
            doc.save()

            add_document_to_queue(doc)

            return HttpResponseRedirect(reverse('course_show', args=[course.slug]))

    else:
        form = UploadFileForm()

    return render(request, 'document_upload.html', {
        'form': form,
        'parent': parentNode,
    })


@login_required
def document_edit(request, document_id):
    doc = get_object_or_404(Document, id=document_id)

    if request.user != doc.user and not request.user.is_moderator(doc.parent):
        return HttpResponse('<h1>403</h1>', status=403)

    if request.method == 'POST':
        form = FileForm(request.POST)

        if form.is_valid():
            doc.name = form.cleaned_data['name']
            doc.description = form.cleaned_data['description']

            doc.keywords.clear()
            doc.add_keywords(*form.cleaned_data['tags'])

            doc.year = form.cleaned_data['year']
            doc.save()

            return HttpResponseRedirect(reverse('document_show', args=[doc.id]))

    else:
        form = FileForm({
            'name': doc.name,
            'description': doc.description,
            'year': doc.year,
            'tags': doc.keywords.all()
        })

    return render(request, 'document_edit.html', {
        'form': form,
        'doc': doc,
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
    with open(doc.original) as fd:
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
        "is_moderator": request.user.is_moderator(document.parent),
        "page_set": list(document.page_set.all()),
    }
    document.views = F('views') + 1
    document.save(update_fields=['views'])
    return render(request, "viewer.html", context)
