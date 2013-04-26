# Copyright 2012, hast. All rights reserved.
#
# This program is free software: you can redistribute it and/or modify it
# under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or (at
# your option) any later version.

from re import match, sub
from django.utils.html import escape
from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404, render
from django.http import HttpResponse, HttpResponseRedirect
from documents.models import Document, PendingDocument, Page
from documents.forms import UploadFileForm
from notify.models import PreNotification


def upload_file(request):
    form = UploadFileForm(request.POST, request.FILES)

    if form.is_valid() and match(r'.*\.[pP][dD][fF]$',
                                 request.FILES['file'].name):
        name = sub(r'\.[Pp][Dd][Ff]$', '', request.FILES['file'].name)
        #name = escape(name.lower().replace(' ', '_'))
        name = escape(name.lower())
        description = escape(form.cleaned_data['description'])
        course = form.cleaned_data['course']
        doc = Document.objects.create(user=request.user.get_profile(),
                                      name=name, description=description)
        course.add_child(doc)
        url = '/tmp/TMP402_%d.pdf' % doc.id
        tmp_doc = open(url, 'w')
        tmp_doc.write(request.FILES['file'].read())
        tmp_doc.close()
        PendingDocument.objects.create(document=doc, state="queued",
                                       url='file://' + url)
        PreNotification.objects.create(
            node=doc, 
            text="Nouveau document: "+name[:50],
            url=reverse('document_show', args=[doc.id]),
            user=request.user
        )
        return HttpResponseRedirect(reverse('course_show', args=[course.slug]))
    return HttpResponse('form invalid', 'text/html')

def document_download(request, id):
    doc = get_object_or_404(Document, id=id)
    with open(doc.staticfile) as fd:
        body = fd.read()
    response = HttpResponse(body, content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="%s.pdf"'%(doc.name)
    doc.download += 1
    doc.save()
    return response


def document_show(request,id):
    document = get_object_or_404(Document, id=id)

    children = document.children()
    document.page_set = children.instance_of(Page)

    context = {"object": document,
                "parent": document.parent}
    document.view += 1
    document.save()
    return render(request, "viewer.html", context)