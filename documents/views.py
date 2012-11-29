# Copyright 2012, hast. All rights reserved.
#
# This program is free software: you can redistribute it and/or modify it
# under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or (at
# your option) any later version.

from re import match, sub
from django.utils.html import escape
from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from documents.models import Document, PendingDocument
from documents.forms import UploadFileForm
from tree.models import Course


def upload_file(request, slug):
    form = UploadFileForm(request.POST, request.FILES)

    if form.is_valid() and match(r'.*\.[pP][dD][fF]$',
                                 request.FILES['file'].name):
        name = sub(r'\.[Pp][Dd][Ff]$', '', request.FILES['file'].name)
        name = escape(name.lower().replace(' ', '_'))
        description = escape(form.cleaned_data['description'])
        course = get_object_or_404(Course, slug=slug)
        doc = Document.objects.create(user=request.user.get_profile(),
                                     reference=course, name=name, 
                                     description=description)

        url = '/tmp/TMP402_%d.pdf' % doc.id
        tmp_doc = open(url, 'w')
        tmp_doc.write(request.FILES['file'].read())
        tmp_doc.close()
        PendingDocument.objects.create(document=doc, state="queued",
                                       url='file://' + url)
        return HttpResponseRedirect(reverse('course_show', args=[slug]))
    return HttpResponse('form invalid', 'text/html')

