from django.conf.urls import url
import documents.views

urlpatterns = [
    url(r"^upload/(?P<slug>[\w-]+)$",
        documents.views.upload_file,
        name="document_put"),

    url(r"^multiple_upload/(?P<slug>[\w-]+)$",
        documents.views.upload_multiple_files,
        name="document_put_multiple"),

    url(r"^(?P<pk>\d+)/edit$",
        documents.views.document_edit,
        name="document_edit"),

    url(r"^(?P<pk>\d+)/reupload$",
        documents.views.document_reupload,
        name="document_reupload"),

    url(r"^(?P<pk>\d+)$",
        documents.views.document_show,
        name="document_show"),
]
