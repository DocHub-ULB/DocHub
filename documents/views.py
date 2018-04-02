# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import os
import uuid
import unicodedata

from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404, render
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.db.models import F
from django.conf import settings

from actstream import action

from documents.models import Document
from documents.forms import FileForm, ReUploadForm
from tags.models import Tag
from catalog.models import Course


@login_required
def upload_file(request, slug):
    course = get_object_or_404(Course, slug=slug)

    return render(request, 'documents/document_upload.html', {
        'course': course,
        'DROPBOX_CHOOSER_KEY': getattr(settings, 'DROPBOX_CHOOSER_KEY', 'NO_KEY_PROVIDED'),
        'GOOGLE_DRIVE_CHOOSER_CLIENT_ID': getattr(settings, 'GOOGLE_DRIVE_CHOOSER_CLIENT_ID', 'NO_KEY_PROVIDED'),
        'GOOGLE_DRIVE_CHOOSER_API_KEY': getattr(settings, 'GOOGLE_DRIVE_CHOOSER_API_KEY', 'NO_KEY_PROVIDED'),
    })


@login_required
def document_edit(request, pk):
    doc = get_object_or_404(Document, id=pk)

    if not request.user.write_perm(obj=doc):
        return HttpResponse('You may not edit this document.', status=403)

    if request.method == 'POST':
        form = FileForm(request.POST)

        if form.is_valid():
            doc.name = form.cleaned_data['name']
            doc.description = form.cleaned_data['description']

            doc.tags.clear()
            for tag in form.cleaned_data['tags']:
                doc.tags.add(Tag.objects.get(name=tag))

            doc.save()

            action.send(request.user, verb="a édité", action_object=doc, target=doc.course)

            return HttpResponseRedirect(reverse('document_show', args=[doc.id]))

    else:
        form = FileForm({
            'name': doc.name,
            'description': doc.description,
            'tags': doc.tags.all()
        })

    return render(request, 'documents/document_edit.html', {
        'form': form,
        'doc': doc,
    })


@login_required
def document_reupload(request, pk):
    document = get_object_or_404(Document, pk=pk)

    if not request.user.write_perm(obj=document):
        return HttpResponse('You may not edit this document.', status=403)

    if document.state != "DONE":
        return HttpResponse('You may not edit this document while it is processing.', status=403)

    if request.method == 'POST':
        form = ReUploadForm(request.POST, request.FILES)

        if form.is_valid():
            file = request.FILES['file']
            name, extension = os.path.splitext(file.name)

            document.pdf.delete(save=False)
            document.original.delete(save=False)

            document.original.save(str(uuid.uuid4()) + extension, file)

            document.state = "PREPARING"
            document.save()

            document.reprocess(force=True)

            action.send(
                request.user,
                verb="a uploadé une nouvelle version de",
                action_object=document,
                target=document.course
            )

            return HttpResponseRedirect(reverse('course_show', args=(document.course.slug,)))

    else:
        form = ReUploadForm()

    return render(request, 'documents/document_reupload.html', {'form': form, 'document': document})


@login_required
def document_download(request, pk):
    doc = get_object_or_404(Document, pk=pk)
    body = doc.pdf.read()
    safe_name = unicodedata.normalize("NFKD", doc.name)

    response = HttpResponse(body, content_type='application/pdf')
    response['Content-Disposition'] = ('attachment; filename="%s.pdf"' % safe_name).encode("ascii", "ignore")

    doc.downloads = F('downloads') + 1
    doc.save(update_fields=['downloads'])
    return response


@login_required
def document_download_original(request, pk):
    doc = get_object_or_404(Document, pk=pk)
    body = doc.original.read()
    safe_name = unicodedata.normalize("NFKD", doc.name)

    response = HttpResponse(body, content_type='application/octet-stream')
    response['Content-Description'] = 'File Transfer'
    response['Content-Transfer-Encoding'] = 'binary'
    response['Content-Disposition'] = 'attachment; filename="{}{}"'.format(safe_name, doc.file_type).encode("ascii", "ignore")

    doc.downloads = F('downloads') + 1
    doc.save(update_fields=['downloads'])
    return response


def document_show(request, pk):
    document = get_object_or_404(Document, pk=pk)

    if not request.user.is_authenticated():
        return render(request, "documents/noauth/viewer.html", {"document": document})

    if document.state != "DONE":
        return HttpResponseRedirect(reverse('course_show', args=(document.course.slug,)))

    context = {
        "document": document,
    }

    document.views = F('views') + 1
    document.save(update_fields=['views'])

    return render(request, "documents/viewer.html", context)
