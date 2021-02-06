from django.urls import path
import documents.views

urlpatterns = [
    path("upload/<slug:slug>",
        documents.views.upload_file,
        name="document_put"),

    path("multiple_upload/<slug:slug>",
        documents.views.upload_multiple_files,
        name="document_put_multiple"),

    path("<int:pk>/edit",
        documents.views.document_edit,
        name="document_edit"),

    path("<int:pk>/reupload",
        documents.views.document_reupload,
        name="document_reupload"),

    path("<int:pk>",
        documents.views.document_show,
        name="document_show"),
]
