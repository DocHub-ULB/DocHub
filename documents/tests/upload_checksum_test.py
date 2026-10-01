import hashlib
from unittest.mock import patch

import pytest
from bs4 import BeautifulSoup
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse

from catalog.models import Course
from documents.logic import add_file_to_course
from documents.models import Document

pytestmark = pytest.mark.django_db

CONTENT = b"An uploaded document" * 10000
DIGEST = hashlib.md5(CONTENT).hexdigest()


@pytest.fixture(autouse=True)
def local_storage(settings, tmp_path):
    settings.MEDIA_ROOT = tmp_path
    settings.STORAGES = {
        **settings.STORAGES,
        "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    }


@pytest.fixture
def course():
    return Course.objects.create(name="Test Course", slug="info-f101")


@pytest.fixture
def create_document(user, course):
    def create(
        *, name: str = "Notes de cours", content: bytes = CONTENT, hidden: bool = False
    ) -> Document:
        document = add_file_to_course(
            file=SimpleUploadedFile("notes.pdf", content),
            name=name,
            extension=".pdf",
            course=course,
            tags=[],
            user=user,
        )
        assert document is not None
        document.state = Document.DocumentState.DONE
        document.hidden = hidden
        document.save()
        return document

    return create


def uploaded_file():
    return SimpleUploadedFile("notes.pdf", CONTENT)


def test_upload_saves_checksum_and_complete_file(client, user, course):
    client.force_login(user)
    with patch("documents.models.process_document.delay") as queue:
        response = client.post(
            reverse("document_put", args=[course.slug]),
            {"file": uploaded_file(), "name": "Notes"},
        )
    assert response.status_code == 302
    document = Document.objects.get(course=course)
    assert document.md5 == DIGEST
    assert document.original.read() == CONTENT
    queue.assert_called_once_with(document.pk)


def test_duplicate_upload_is_rejected_before_saving(
    client, user, course, create_document
):
    existing = create_document()
    client.force_login(user)
    with patch("documents.models.process_document.delay") as queue:
        response = client.post(
            reverse("document_put", args=[course.slug]),
            {"file": uploaded_file(), "name": "Notes"},
        )
    assert response.status_code == 422
    assert "déjà sur DocHub" in response.context["form"].errors["file"][0]
    page = BeautifulSoup(response.content, "html.parser")
    link = page.select_one(f'.upload-error a[href="{existing.get_absolute_url()}"]')
    assert link is not None
    assert link.get_text() == existing.name
    assert Document.objects.count() == 1
    queue.assert_not_called()


def test_reupload_replaces_file_and_updates_checksum(client, user, create_document):
    document = create_document(content=b"old contents")

    client.force_login(user)
    with patch("documents.models.process_document.delay") as queue:
        response = client.post(
            reverse("document_reupload", args=[document.pk]),
            {"file": uploaded_file()},
        )

    assert response.status_code == 302
    document.refresh_from_db()
    assert document.md5 == DIGEST
    assert document.original.read() == CONTENT
    assert document.state == Document.DocumentState.IN_QUEUE
    queue.assert_called_once_with(document.pk)


def test_duplicate_reupload_preserves_existing_file(client, user, create_document):
    document = create_document(content=b"old contents")
    old_name = document.original.name
    old_checksum = document.md5

    existing = create_document(name="Duplicate")

    client.force_login(user)
    with patch("documents.models.process_document.delay") as queue:
        response = client.post(
            reverse("document_reupload", args=[document.pk]),
            {"file": uploaded_file()},
        )

    assert response.status_code == 422
    page = BeautifulSoup(response.content, "html.parser")
    link = page.select_one(f'.upload-error a[href="{existing.get_absolute_url()}"]')
    assert link is not None
    assert link.get_text() == existing.name
    document.refresh_from_db()
    assert document.original.name == old_name
    assert document.original.read() == b"old contents"
    assert document.md5 == old_checksum
    assert document.state == Document.DocumentState.DONE
    queue.assert_not_called()


def test_hidden_duplicate_is_replaced(client, user, course, create_document):
    hidden = create_document(hidden=True)
    client.force_login(user)
    with patch("documents.models.process_document.delay"):
        response = client.post(
            reverse("document_put", args=[course.slug]),
            {"file": uploaded_file(), "name": "Notes"},
        )
    assert response.status_code == 302
    document = Document.objects.exclude(pk=hidden.pk).get()
    assert not Document.objects.filter(pk=hidden.pk).exists()
    assert Document.objects.filter(pk=document.pk, md5=DIGEST).exists()


def test_reupload_replaces_hidden_duplicate(client, user, create_document):
    document = create_document(content=b"old contents", hidden=True)
    hidden = create_document(name="Hidden duplicate", hidden=True)

    client.force_login(user)
    with patch("documents.models.process_document.delay"):
        response = client.post(
            reverse("document_reupload", args=[document.pk]),
            {"file": uploaded_file()},
        )
    assert response.status_code == 302
    assert not Document.objects.filter(pk=hidden.pk).exists()
    assert Document.objects.filter(pk=document.pk, md5=DIGEST).exists()
