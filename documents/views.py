import os
import uuid

from django.urls import reverse
from django.shortcuts import get_object_or_404, render
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.db.models import F
from django.conf import settings


from actstream import action

from documents.models import Document
from catalog.models import Course
from documents.forms import UploadFileForm, FileForm, MultipleUploadFileForm, ReUploadForm
from tags.models import Tag
from documents import logic


@login_required
def upload_file(request, slug):
    course = get_object_or_404(Course, slug=slug)

    if request.method == 'POST':
        if settings.READ_ONLY:
            return HttpResponse('Upload is disabled for a few hours', status=401)

        form = UploadFileForm(request.POST, request.FILES)

        if form.is_valid():
            file = request.FILES['file']

            name, extension = os.path.splitext(file.name)
            name = logic.clean_filename(name)

            if form.cleaned_data['name']:
                name = form.cleaned_data['name']

            document = logic.add_file_to_course(
                file=file,
                name=name,
                extension=extension,
                course=course,
                tags=form.cleaned_data['tags'],
                user=request.user
            )

            document.description = form.cleaned_data['description']
            document.save()

            document.add_to_queue()

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
def upload_multiple_files(request, slug):
    course = get_object_or_404(Course, slug=slug)

    if request.method == 'POST':
        if settings.READ_ONLY:
            return HttpResponse('Upload is disabled for a few hours', status=401)

        form = MultipleUploadFileForm(request.POST, request.FILES)

        if form.is_valid():
            for attachment in form.cleaned_data['files']:
                name, extension = os.path.splitext(attachment.name)
                name = logic.clean_filename(name)

                document = logic.add_file_to_course(
                    file=attachment,
                    name=name,
                    extension=extension,
                    course=course,
                    tags=[],
                    user=request.user
                )
                document.add_to_queue()

            return HttpResponseRedirect(reverse('course_show', args=[course.slug]))
    return HttpResponseRedirect(reverse('document_put', args=(course.slug,)))


@login_required
def document_edit(request, pk):
    doc = get_object_or_404(Document, id=pk)

    if not request.user.write_perm(obj=doc):
        return HttpResponse('You may not edit this document.', status=403)

    if request.method == 'POST':
        if settings.READ_ONLY:
            return HttpResponse('Upload is disabled for a few hours', status=401)

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

    if document.state != Document.DocumentState.DONE:
        return HttpResponse('You may not edit this document while it is processing.', status=403)

    if request.method == 'POST':
        if settings.READ_ONLY:
            return HttpResponse('Upload is disabled for a few hours', status=401)

        form = ReUploadForm(request.POST, request.FILES)

        if form.is_valid():
            file = request.FILES['file']
            name, extension = os.path.splitext(file.name)

            document.pdf.delete(save=False)
            document.original.delete(save=False)

            document.original.save(str(uuid.uuid4()) + extension, file)

            document.state = Document.DocumentState.PREPARING
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


def document_show(request, pk):
    document = get_object_or_404(Document, pk=pk)

    if not request.user.is_authenticated:
        return render(request, "documents/noauth/viewer.html", {"document": document})

    if document.state != Document.DocumentState.DONE:
        return HttpResponseRedirect(reverse('course_show', args=(document.course.slug,)))

    context = {
        "document": document,
    }

    document.views = F('views') + 1
    document.save(update_fields=['views'])

    return render(request, "documents/viewer.html", context)
