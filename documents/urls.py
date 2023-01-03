from django.urls import path

import documents.views

urlpatterns = [
    path("upload/<slug:slug>", documents.views.upload_file, name="document_put"),
    path(
        "submit-bulk/<slug:slug>",
        documents.views.submit_bulk,
        name="document_submit_bulk",
    ),
    path("<int:pk>/edit", documents.views.document_edit, name="document_edit"),
    path(
        "<int:pk>/reupload", documents.views.document_reupload, name="document_reupload"
    ),
    path("<int:pk>", documents.views.document_show, name="document_show"),
    path("<int:pk>/vote", documents.views.document_vote, name="document_vote"),
    path(
        "<int:pk>/original",
        documents.views.document_original_file,
        name="document_original",
    ),
    path("<int:pk>/pdf", documents.views.document_pdf_file, name="document_pdf"),
]
