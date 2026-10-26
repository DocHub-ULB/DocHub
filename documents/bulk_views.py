import json
import os

from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.views.decorators.http import require_GET, require_POST

from catalog.models import Course
from documents import logic
from documents.bulk import plan_bulk_upload
from documents.exceptions import ExisingChecksum
from documents.forms import (
    BulkFilesForm,
    BulkUploadCheckForm,
    BulkUploadFileForm,
    MultipleUploadFileForm,
    UploadFileForm,
)
from documents.models import BulkDocuments
from stats.models import DailyStat, Metric


@login_required
@require_GET
def bulk_upload(request):
    """Share a whole folder, with one subfolder per course. A wizard in 4 steps.

    Step 1 explains how to prepare the folder. Step 2 picks the folder: the
    page then posts the paths and sizes of the files, and we show the plan
    (step 3), so that the user can fix the folder before a long upload. The
    preview includes the upload queue and a prepared progress screen (step 4).
    The send button shows that screen and sends the files one by one to
    bulk_upload_file, without another request to prepare the upload.
    Turbo replaces the picker with the preview. The preparation and picker
    use full page loads so browser Back can warn before an upload is interrupted.
    """
    return render(request, "documents/bulk_upload.html", {"step": 1})


@login_required
@require_GET
def bulk_upload_pick(request):
    """Pick the folder."""
    return render(request, "documents/bulk_upload.html", {"step": 2})


@login_required
@require_POST
def bulk_upload_check(request):
    """Check the folder and prepare the preview, upload queue, and progress screen.

    If the list of files is not valid, we show step 2 again with the errors.
    """
    template = "documents/bulk_upload.html#wizard"
    form = BulkUploadCheckForm(request.POST)
    if not form.is_valid():
        return render(
            request,
            template,
            {"step": 2, "errors": form.errors["entries"]},
            status=422,
        )
    entries = form.cleaned_data["entries"]
    plan = plan_bulk_upload(entries)
    queue = [
        {
            "path": file.path,
            "url": reverse("document_bulk_upload_file", args=[folder.course.slug]),
        }
        for folder in plan.ready_folders
        for file in folder.ready_files
    ]
    return render(
        request,
        template,
        {
            "step": 3,
            "plan": plan,
            "folder_name": entries[0][0].split("/")[0],
            "queue": json.dumps(queue),
        },
    )


@login_required
@require_POST
def bulk_upload_file(request, slug):
    """Receive one file of a bulk upload.

    We answer 201 when we add the document, 409 when it is already on DocHub.
    For any other answer, the page stops the upload.
    """
    course = get_object_or_404(Course, slug=slug)
    form = BulkUploadFileForm(request.POST, request.FILES)
    if not form.is_valid():
        return HttpResponseBadRequest()

    DailyStat.track(Metric.UPLOAD_SUBMIT)
    file = form.cleaned_data["file"]
    try:
        document = logic.add_file_to_course(
            file=file,
            name=logic.document_title(file.name, course),
            extension=os.path.splitext(file.name)[1],
            course=course,
            tags=logic.document_tags(file.name),
            user=request.user,
        )
    except ExisingChecksum:
        return HttpResponse(status=409)

    document.add_to_queue()
    return HttpResponse(status=201)


@login_required
def submit_bulk_url(request, slug):
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
