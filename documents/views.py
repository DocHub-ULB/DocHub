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

from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404, render
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.db.models import F

from documents.models import Document
from catalog.models import Course
from documents.forms import UploadFileForm, FileForm, MultipleUploadFileForm
from www.helpers import year_choices
from telepathy.forms import NewThreadForm
from tags.models import Tag

from cycle import add_document_to_queue


@login_required
def upload_file(request, course_slug):
    course = get_object_or_404(Course, slug=course_slug)

    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)

        if form.is_valid():
            if len(form.cleaned_data['name']) > 0:
                name = form.cleaned_data['name']
            else:
                name, _ = os.path.splitext(request.FILES['file'].name)
                name = name.lower().replace('_', ' ')

            extension = os.path.splitext(request.FILES['file'].name)[1].lower()
            description = form.cleaned_data['description']

            doc = Document.objects.create(
                user=request.user,
                name=name,
                course=course,
                description=description,
                state="PREPARING",
                file_type=extension
            )
            doc.original.save(str(uuid.uuid4()) + extension, request.FILES['file'])
            doc.save()

            for tag in form.cleaned_data['tags']:
                doc.tags.add(Tag.objects.get(name=tag))

            doc.year = form.cleaned_data['year']

            doc.state = 'READY_TO_QUEUE'
            doc.save()

            add_document_to_queue(doc)

            return HttpResponseRedirect(reverse('course_show', args=[course.slug]))

    else:
        form = UploadFileForm()
        multiform = MultipleUploadFileForm()

    return render(request, 'documents/document_upload.html', {
        'form': form,
        'multiform': multiform,
        'course': course,
    })


@login_required
def upload_multiple_files(request, course_slug):
    course = get_object_or_404(Course, slug=course_slug)

    if request.method == 'POST':
        form = MultipleUploadFileForm(request.POST, request.FILES)

        if form.is_valid():
            for attachment in form.cleaned_data['files']:
                name, _ = os.path.splitext(attachment.name)
                name = name.lower()

                extension = os.path.splitext(attachment.name)[1].lower()
                description = ""

                doc = Document.objects.create(
                    user=request.user,
                    name=name,
                    course=course,
                    description=description,
                    state="PREPARING",
                    file_type=extension
                )
                doc.original.save(str(uuid.uuid4()) + extension, attachment)
                doc.year = year_choices(1)[0][0]
                doc.save()

                course.add_child(doc)
                doc.state = 'READY_TO_QUEUE'
                doc.save()
                add_document_to_queue(doc)

            return HttpResponseRedirect(reverse('course_show', args=[course.slug]))
    return HttpResponseRedirect(reverse('document_put', args=(course.id,)))


@login_required
def document_edit(request, document_id):
    doc = get_object_or_404(Document, id=document_id)

    if request.user != doc.user:
        return HttpResponse('You may not edit this document.', status=403)

    if request.method == 'POST':
        form = FileForm(request.POST)

        if form.is_valid():
            doc.name = form.cleaned_data['name']
            doc.description = form.cleaned_data['description']

            doc.tags.clear()
            for tag in form.cleaned_data['tags']:
                doc.tags.add(Tag.objects.get(name=tag))

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

    return render(request, 'documents/document_edit.html', {
        'form': form,
        'doc': doc,
    })


@login_required
def document_download(request, id):
    doc = get_object_or_404(Document, id=id)
    body = doc.pdf.read()
    response = HttpResponse(body, content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="%s.pdf"' % (doc.name)

    doc.downloads = F('downloads') + 1
    doc.save(update_fields=['downloads'])
    return response


@login_required
def document_download_original(request, id):
    doc = get_object_or_404(Document, id=id)
    body = doc.original.read()
    response = HttpResponse(body, content_type='application/octet-stream')
    response['Content-Description'] = 'File Transfer'
    response['Content-Transfer-Encoding'] = 'binary'
    response['Content-Disposition'] = 'attachment; filename="{}{}"'.format(doc.name, doc.file_type)

    doc.downloads = F('downloads') + 1
    doc.save(update_fields=['downloads'])
    return response


@login_required
def document_show(request, id):
    document = get_object_or_404(Document, id=id)

    context = {
        "document": document,
        "form": NewThreadForm(),
    }

    document.views = F('views') + 1
    document.save(update_fields=['views'])

    return render(request, "documents/viewer.html", context)
