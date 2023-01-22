import os
import uuid

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import F
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.clickjacking import xframe_options_sameorigin
from django.views.decorators.http import require_POST

from catalog.models import Course
from catalog.views import slug_redirect
from documents import logic
from documents.forms import (
    BulkFilesForm,
    FileForm,
    MultipleUploadFileForm,
    ReUploadForm,
    UploadFileForm,
)
from documents.models import BulkDocuments, Document, Vote
from moderation.models import ModerationLog
from tags.models import Tag


@login_required
@slug_redirect
def upload_file(request, slug):
    course = get_object_or_404(Course, slug=slug)

    if request.method == "POST":
        if settings.READ_ONLY:
            return HttpResponse("Upload is disabled for a few hours", status=401)

        form = UploadFileForm(request.POST, request.FILES)

        if form.is_valid():
            file = request.FILES["file"]

            name, extension = os.path.splitext(file.name)
            name = logic.clean_filename(name)

            if form.cleaned_data["name"]:
                name = form.cleaned_data["name"]

            document = logic.add_file_to_course(
                file=file,
                name=name,
                extension=extension,
                course=course,
                tags=form.cleaned_data["tags"],
                user=request.user,
            )

            document.description = form.cleaned_data["description"]
            document.save()

            document.add_to_queue()

            return HttpResponseRedirect(
                reverse("catalog:course_show", args=[course.slug])
            )

    else:
        form = UploadFileForm()

    multiform = MultipleUploadFileForm()

    return render(
        request,
        "documents/document_upload.html",
        {
            "form": form,
            "multiform": multiform,
            "course": course,
        },
    )


@login_required
def document_edit(request, pk):
    doc = get_object_or_404(Document, id=pk)

    if not request.user.write_perm(obj=doc):
        return HttpResponse("You may not edit this document.", status=403)

    if request.method == "POST":
        if settings.READ_ONLY:
            return HttpResponse("Upload is disabled for a few hours", status=401)

        if "delete" in request.POST:
            if request.user != doc.user:
                ModerationLog.track(
                    user=request.user,
                    content_object=doc,
                    values={"hidden": (doc.hidden, True)},
                )

            doc.hidden = True
            doc.save()
            # TODO: use the messages in the templates (later)
            messages.success(request, "Le document a bien été caché !")
            return HttpResponseRedirect(
                reverse("catalog:course_show", args=[doc.course.slug])
            )

        form = FileForm(request.POST)

        if form.is_valid():
            if request.user != doc.user:
                ModerationLog.track(
                    user=request.user,
                    content_object=doc,
                    values={
                        "name": (doc.name, form.cleaned_data["name"]),
                        "description": (
                            doc.description,
                            form.cleaned_data["description"],
                        ),
                        "tags": (doc.tags.all(), form.cleaned_data["tags"]),
                    },
                )

            doc.name = form.cleaned_data["name"]
            doc.description = form.cleaned_data["description"]

            doc.tags.clear()
            for tag in form.cleaned_data["tags"]:
                doc.tags.add(Tag.objects.get(name=tag))

            doc.save()

            return HttpResponseRedirect(reverse("document_show", args=[doc.id]))

    else:
        form = FileForm(
            {"name": doc.name, "description": doc.description, "tags": doc.tags.all()}
        )

    return render(
        request,
        "documents/document_edit.html",
        {
            "form": form,
            "doc": doc,
        },
    )


@login_required
def document_reupload(request, pk):
    document = get_object_or_404(Document, pk=pk)

    if not request.user.write_perm(obj=document):
        return HttpResponse("You may not edit this document.", status=403)
    # FIXME: log moderation action

    if document.state != Document.DocumentState.DONE:
        return HttpResponse(
            "You may not edit this document while it is processing.", status=403
        )

    if request.method == "POST":
        if settings.READ_ONLY:
            return HttpResponse("Upload is disabled for a few hours", status=401)

        form = ReUploadForm(request.POST, request.FILES)

        if form.is_valid():
            file = request.FILES["file"]
            name, extension = os.path.splitext(file.name)

            document.pdf.delete(save=False)
            document.original.delete(save=False)

            document.original.save(str(uuid.uuid4()) + extension, file)

            document.state = Document.DocumentState.PREPARING
            document.save()

            document.reprocess(force=True)

            # TODO Log new version upload
            # action.send(
            #     request.user,
            #     verb="a uploadé une nouvelle version de",
            #     action_object=document,
            #     target=document.course,
            # )

            return HttpResponseRedirect(
                reverse("catalog:course_show", args=(document.course.slug,))
            )

    else:
        form = ReUploadForm()

    return render(
        request,
        "documents/document_reupload.html",
        {"form": form, "document": document},
    )


def document_show(request, pk):
    document = get_object_or_404(Document, pk=pk)

    if not request.user.is_authenticated:
        return render(request, "documents/noauth/viewer.html", {"document": document})

    if document.state == Document.DocumentState.DONE:
        document.views = F("views") + 1
        document.save(update_fields=["views"])

    context = {
        "document": document,
        "user_vote": document.vote_set.filter(user=request.user).first(),
    }

    return render(request, "documents/viewer.html", context)


@login_required
@require_POST
def document_vote(request, pk):
    document = get_object_or_404(Document, pk=pk)

    vote, created = Vote.objects.get_or_create(document=document, user=request.user)
    if vote.vote_type == request.POST.get("vote_type"):
        vote.delete()
    else:
        vote.vote_type = request.POST.get("vote_type")
        vote.save()

    return redirect(document.get_absolute_url())


@login_required
def document_original_file(request, pk):
    document = get_object_or_404(Document, pk=pk)

    body = document.original.read()

    response = HttpResponse(body, content_type="application/octet-stream")
    response["Content-Description"] = "File Transfer"
    response["Content-Transfer-Encoding"] = "binary"
    response[
        "Content-Disposition"
    ] = f'attachment; filename="{document.safe_name}{document.file_type}"'.encode(
        "ascii", "ignore"
    )

    document.downloads = F("downloads") + 1
    document.save(update_fields=["downloads"])
    return response


@xframe_options_sameorigin
@login_required
def document_pdf_file(request, pk):
    document = get_object_or_404(Document, pk=pk)
    body = document.pdf.read()

    response = HttpResponse(body, content_type="application/pdf")
    content_disposition = 'filename="%s.pdf"' % document.safe_name
    if "embed" not in request.GET:
        content_disposition = "attachment; " + content_disposition

    response["Content-Disposition"] = content_disposition.encode("ascii", "ignore")

    document.downloads = F("views") + 1
    document.save(update_fields=["views"])
    return response


@login_required
def submit_bulk(request, slug):
    course = get_object_or_404(Course, slug=slug)

    if request.method == "POST":
        form = BulkFilesForm(request.POST)

        if form.is_valid():
            BulkDocuments.objects.create(
                url=form.cleaned_data["url"], course=course, user=request.user
            )

            return render(
                request,
                "documents/document_bulk.html",
                {
                    "course": course,
                },
            )

    return HttpResponseRedirect(reverse("document_put", args=[course.slug]))
