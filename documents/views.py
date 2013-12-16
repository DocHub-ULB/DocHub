# -*- coding: utf-8 -*-
from __future__ import unicode_literals

# Copyright 2012, hast. All rights reserved.
#
# This program is free software: you can redistribute it and/or modify it
# under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or (at
# your option) any later version.

from django.utils.html import escape
from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404, render
from django.http import HttpResponse, HttpResponseRedirect
from documents.models import Document, Page #,PendingDocument
from documents.forms import UploadFileForm

from celery import chain
from documents.tasks import download, pdf_lenght, preview_pdf, finish_file


def upload_file(request):
    form = UploadFileForm(request.POST, request.FILES)

    if not form.is_valid():
        return HttpResponse('form invalid'+str(form.errors), 'text/html')

    if len(form.cleaned_data['name'])>0:
        name = escape(form.cleaned_data['name'])
    else:
        name = escape(request.FILES['file'].name[:-4].lower())

    description = escape(form.cleaned_data['description'])
    course = form.cleaned_data['course']


    doc = Document.objects.create(user=request.user.get_profile(),
                                  name=name, description=description, state="queued")
    course.add_child(doc)

    tmp_file = '/tmp/TMP402_%d.pdf' % doc.id
    source = 'file://' + tmp_file
    doc.source = source 
    doc.save()

    tmp_doc = open(tmp_file, 'w')
    tmp_doc.write(request.FILES['file'].read())
    tmp_doc.close()
    
    c = chain(download.s(doc.id), pdf_lenght.s(), preview_pdf.s(), finish_file.s())
    c.delay()

    return HttpResponseRedirect(reverse('course_show', args=[course.slug]))

def document_download(request, id):
    doc = get_object_or_404(Document, id=id)
    with open(doc.staticfile) as fd:
        body = fd.read()
    response = HttpResponse(body, content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="%s.pdf"'%(doc.name)
    doc.downloads += 1
    doc.save()
    return response


def document_show(request,id):
    document = get_object_or_404(Document, id=id)

    children = document.children()
    document.page_set = children.instance_of(Page)

    context = {"object": document,
                "parent": document.parent}
    document.views += 1
    document.save()
    return render(request, "viewer.html", context)