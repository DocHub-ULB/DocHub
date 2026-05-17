import os
import uuid

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.contenttypes.models import ContentType
from django.db.models import F
from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.clickjacking import xframe_options_sameorigin
from django.views.decorators.http import require_POST

from catalog.models import Course
from catalog.views import slug_redirect
from documents import logic
from documents.forms import (
    BulkFilesForm,
    DocumentForm,
    DocumentReportForm,
    MultipleUploadFileForm,
    ReUploadForm,
    UploadFileForm,
)
from documents.models import BulkDocuments, Document, Vote
from moderation.models import ModerationLog
from stats.models import DailyStat, Metric


def _document_form_for_user(user, document, *args, **kwargs):
    form = DocumentForm(*args, instance=document, **kwargs)
    if not user.moderation_perm(document):
        form.fields.pop("staff_pick", None)
    return form


@login_required
@slug_redirect
def upload_file(request, slug):
    course = get_object_or_404(Course, slug=slug)

    if request.method == "POST":
        if settings.READ_ONLY:
            return HttpResponse("Upload is disabled for a few hours", status=401)

        DailyStat.track(Metric.UPLOAD_SUBMIT)

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
    bulk_form = BulkFilesForm()

    return render(
        request,
        "documents/document_upload.html",
        {
            "form": form,
            "multiform": multiform,
            "bulk_form": bulk_form,
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

        DailyStat.track(Metric.DOCUMENT_EDIT)

        if "hide" in request.POST:
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

        elif "unhide" in request.POST:
            if request.user != doc.user:
                ModerationLog.track(
                    user=request.user,
                    content_object=doc,
                    values={"hidden": (doc.hidden, False)},
                )

            doc.hidden = False
            doc.save()
            # TODO: use the messages in the templates (later)
            messages.success(request, "Le document a ete rendu visible !")
            return HttpResponseRedirect(
                reverse("catalog:course_show", args=[doc.course.slug])
            )

        old_name = doc.name
        old_description = doc.description
        old_tags = list(doc.tags.all())
        old_staff_pick = doc.staff_pick

        can_staff_pick = request.user.moderation_perm(doc)
        form = _document_form_for_user(request.user, doc, request.POST)

        if form.is_valid():
            if request.user != doc.user:
                values = {
                    "name": (old_name, form.cleaned_data["name"]),
                    "description": (
                        old_description,
                        form.cleaned_data["description"],
                    ),
                    "tags": (old_tags, form.cleaned_data["tags"]),
                }
                if can_staff_pick:
                    values["staff_pick"] = (
                        old_staff_pick,
                        form.cleaned_data["staff_pick"],
                    )
                ModerationLog.track(
                    user=request.user, content_object=doc, values=values
                )
            elif can_staff_pick:
                ModerationLog.track(
                    user=request.user,
                    content_object=doc,
                    values={
                        "staff_pick": (
                            old_staff_pick,
                            form.cleaned_data["staff_pick"],
                        ),
                    },
                )

            # TODO Log edit
            # action.send(
            #     request.user, verb="a édité", action_object=doc, target=doc.course
            # )

            form.save()
            return HttpResponseRedirect(reverse("document_show", args=[doc.id]))

    else:
        form = _document_form_for_user(request.user, doc)

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

    if document.state != Document.DocumentState.DONE:
        return HttpResponse(
            "You may not edit this document while it is processing.", status=403
        )

    if request.method == "POST":
        if settings.READ_ONLY:
            return HttpResponse("Upload is disabled for a few hours", status=401)

        DailyStat.track(Metric.DOCUMENT_REUPLOAD)

        form = ReUploadForm(request.POST, request.FILES)

        if form.is_valid():
            file = request.FILES["file"]
            _name, extension = os.path.splitext(file.name)

            document.pdf.delete(save=False)
            document.original.delete(save=False)

            document.original.save(str(uuid.uuid4()) + extension, file)

            document.state = Document.DocumentState.PREPARING
            document.save()

            document.reprocess(force=True)

            if request.user != document.user:
                ModerationLog.track(
                    user=request.user,
                    content_object=document,
                    values={"reupload": ("", file.name)},
                )

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
        DailyStat.track(Metric.DOCUMENT_VIEW)

    context = {
        "document": document,
        "user_vote": document.vote_set.filter(user=request.user).first(),
        "form": DocumentReportForm(),
        "has_moderation_history": ModerationLog.objects.filter(
            content_type=ContentType.objects.get_for_model(Document),
            object_id=document.pk,
        ).exists(),
    }

    return render(request, "documents/viewer.html", context)


@login_required
@require_POST
def document_vote(request, pk):
    document = get_object_or_404(Document, pk=pk)

    vote, _created = Vote.objects.get_or_create(document=document, user=request.user)
    if vote.vote_type == request.POST.get("vote_type"):
        vote.delete()
    else:
        vote.vote_type = request.POST.get("vote_type")
        vote.save()

    return redirect(document.get_absolute_url())


@login_required
def document_original_file(request, pk):
    document = get_object_or_404(Document, pk=pk)

    # Check if original file exists
    if not document.original or not document.original.name:
        raise Http404("Le fichier original n'existe pas pour ce document")

    body = document.original.read()

    response = HttpResponse(body, content_type="application/octet-stream")
    response["Content-Description"] = "File Transfer"
    response["Content-Transfer-Encoding"] = "binary"
    response["Content-Disposition"] = (
        f'attachment; filename="{document.safe_name}{document.file_type}"'.encode(
            "ascii", "ignore"
        )
    )

    document.downloads = F("downloads") + 1
    document.save(update_fields=["downloads"])
    DailyStat.track(Metric.DOCUMENT_DOWNLOAD)
    return response


@xframe_options_sameorigin
@login_required
def document_pdf_file(request, pk):
    document = get_object_or_404(Document, pk=pk)

    # Check if PDF file exists
    if not document.pdf or not document.pdf.name:
        raise Http404("Le fichier PDF n'existe pas pour ce document")

    body = document.pdf.read()

    response = HttpResponse(body, content_type="application/pdf")
    content_disposition = 'filename="%s.pdf"' % document.safe_name
    if "embed" not in request.GET:
        content_disposition = "attachment; " + content_disposition

    response["Content-Disposition"] = content_disposition.encode("ascii", "ignore")

    document.downloads = F("views") + 1
    document.save(update_fields=["views"])
    DailyStat.track(Metric.DOCUMENT_DOWNLOAD)
    return response


@login_required
def submit_bulk(request, slug):
    course = get_object_or_404(Course, slug=slug)

    if request.method == "POST":
        form = BulkFilesForm(request.POST)

        if form.is_valid():
            url = form.cleaned_data["url"]

            # Verify Duplicate Submission URL
            if BulkDocuments.objects.filter(
                url=url, course=course, processed=False
            ).exists():
                form.add_error(
                    "url",
                    "Ce lien a déjà été soumis pour ce cours et est en attente de traitement.",
                )
                return render(
                    request,
                    "documents/document_upload.html",
                    {
                        "course": course,
                        "form": UploadFileForm(),
                        "multiform": MultipleUploadFileForm(),
                        "bulk_form": form,
                    },
                    # status=422  mandatory for Turbo: forces the display of validation errors (Turbo ignores 200 codes)
                    status=422,
                )

            # Succes submit URL
            BulkDocuments.objects.create(url=url, course=course, user=request.user)
            success_url = (
                reverse("document_submit_bulk", args=[course.slug]) + "?success=true"
            )
            return HttpResponseRedirect(success_url)

        else:
            # Bad URL submit
            return render(
                request,
                "documents/document_upload.html",
                {
                    "course": course,
                    "form": UploadFileForm(),
                    "multiform": MultipleUploadFileForm(),
                    "bulk_form": form,
                },
                status=422,
            )

    if "success" in request.GET:
        return render(
            request,
            "documents/document_bulk.html",
            {
                "course": course,
            },
        )

    return HttpResponseRedirect(reverse("document_put", args=[course.slug]))


@login_required
def document_report(request, pk):
    document = get_object_or_404(Document, pk=pk)

    if request.method == "POST":
        form = DocumentReportForm(request.POST)

        if form.is_valid():
            report = form.save(commit=False)
            report.user = request.user
            report.document = document
            report.save()

            messages.success(
                request,
                "Ton signalement a bien été enregistré. Merci de ta contribution !",
            )
            return redirect(document.get_absolute_url())

    else:
        form = DocumentReportForm()

    return render(
        request,
        "documents/document_report.html",
        {
            "form": form,
            "document": document,
        },
    )
