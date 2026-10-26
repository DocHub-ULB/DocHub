from django.urls import path

import documents.bulk_views
import documents.views

urlpatterns = [
    path("upload/", documents.views.upload_picker, name="document_upload"),
    path(
        "upload/bulk/",
        documents.bulk_views.bulk_upload,
        name="document_bulk_upload",
    ),
    path(
        "upload/bulk/pick",
        documents.bulk_views.bulk_upload_pick,
        name="document_bulk_upload_pick",
    ),
    path(
        "upload/bulk/check",
        documents.bulk_views.bulk_upload_check,
        name="document_bulk_upload_check",
    ),
    path(
        "upload/bulk/file/<slug:slug>",
        documents.bulk_views.bulk_upload_file,
        name="document_bulk_upload_file",
    ),
    path("upload/<slug:slug>", documents.views.upload_file, name="document_put"),
    path("<int:pk>/edit", documents.views.document_edit, name="document_edit"),
    path(
        "<int:pk>/reupload", documents.views.document_reupload, name="document_reupload"
    ),
    path("<int:pk>", documents.views.document_show, name="document_show"),
    path("<int:pk>/like", documents.views.document_like, name="document_like"),
    path("<int:pk>/report", documents.views.document_report, name="document_report"),
    path(
        "<int:pk>/original",
        documents.views.document_original_file,
        name="document_original",
    ),
    path("<int:pk>/pdf", documents.views.document_pdf_file, name="document_pdf"),
]
