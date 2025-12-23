from django.core.files import File

import celery
import pytest

from documents import tasks
from documents.models import Document
from documents.tasks import mutool_get_pages, process_document
from users.models import User

pytestmark = [pytest.mark.django_db, pytest.mark.celery]


def create_doc(name, ext):
    try:
        user = User.objects.get(netid="test_user")
    except User.DoesNotExist:
        user = User.objects.create_user(netid="test_user")
    doc = Document.objects.create(
        user=user, name=name, state=Document.DocumentState.IN_QUEUE, file_type=ext
    )

    return doc


@pytest.mark.slow
def test_add_to_queue():
    doc = create_doc("Document name", ".pdf")
    with open("documents/tests/files/3pages.pdf", "rb") as fd:
        f = File(fd)
        doc.original.save("silly-unique-deadbeef-file.pdf", f)

    result = process_document.delay(doc.id)
    assert result.status == celery.states.SUCCESS, result.traceback

    doc = Document.objects.get(id=doc.id)  # Get back the updated instance

    assert doc.state == Document.DocumentState.DONE
    assert doc.original.path == doc.pdf.path


@pytest.mark.slow
def test_send_duplicate():
    test_add_to_queue()

    doc = create_doc("Document name2", ".pdf")

    with open("documents/tests/files/3pages.pdf", "rb") as fd:
        f = File(fd)
        doc.original.save("another-uuid-beef-dead.pdf", f)

    result = process_document.delay(doc.id)
    assert result.status == celery.states.FAILURE
    assert "ExisingChecksum" in result.traceback
    assert Document.objects.filter(id=doc.id).count() == 0


# TODO : mock unoserver and provide a fake pdf instead
@pytest.mark.unoserver
@pytest.mark.slow
def test_send_office():
    doc = create_doc("My office doc", ".docx")

    with open("documents/tests/files/2pages.docx", "rb") as fd:
        f = File(fd)
        doc.original.save("silly-unique-deadbeef-file.docx", f)

    result = process_document.delay(doc.id)
    assert result.status == celery.states.SUCCESS, result.traceback

    doc = Document.objects.get(id=doc.id)  # Get back the updated instance

    assert doc.state == Document.DocumentState.DONE
    assert doc.original.path != doc.pdf.path


def test_correct_checksum():
    doc = create_doc("Document name2", ".pdf")

    with open("documents/tests/files/3pages.pdf", "rb") as fd:
        f = File(fd)
        doc.original.save("another-uuid-beef-dead.pdf", f)

    result = tasks.checksum.delay(doc.id)
    assert result.status == celery.states.SUCCESS, result.traceback

    doc = Document.objects.get(id=doc.id)  # Get back the updated instance
    assert doc.md5 == "8be98044ac25f3050b121aceac618823"


def test_duplicate_checksum():
    doc = create_doc("Document name2", ".pdf")
    doc.md5 = "8be98044ac25f3050b121aceac618823"
    doc.save()

    duplicate = create_doc("Document name2", ".pdf")

    with open("documents/tests/files/3pages.pdf", "rb") as fd:
        f = File(fd)
        duplicate.original.save("another-uuid-beef-dead.pdf", f)

    result = tasks.checksum.delay(duplicate.id)
    assert result.status == celery.states.FAILURE
    assert "ExisingChecksum" in result.traceback
    assert Document.objects.filter(id=duplicate.id).count() == 0


def test_duplicate_hidden_checksum():
    doc = create_doc("Document name2", ".pdf")
    doc.md5 = "8be98044ac25f3050b121aceac618823"
    doc.hidden = True
    doc.save()

    duplicate = create_doc("Document name2", ".pdf")

    with open("documents/tests/files/3pages.pdf", "rb") as fd:
        f = File(fd)
        duplicate.original.save("another-uuid-beef-dead.pdf", f)

    result = tasks.checksum.delay(duplicate.id)
    assert result.status == celery.states.SUCCESS, result.traceback
    assert Document.objects.filter(id=duplicate.id).count() == 1
    assert Document.objects.filter(id=doc.id).count() == 0
    assert (
        Document.objects.get(id=duplicate.id).md5 == "8be98044ac25f3050b121aceac618823"
    )


def test_correct_mutool_length():
    doc = create_doc("Document name", ".pdf")

    with open("documents/tests/files/3pages.pdf", "rb") as fd:
        f = File(fd)
        doc.pdf.save("another-uuid-beef-dead.pdf", f)

    assert mutool_get_pages(doc) == 3


def test_correct_length():
    doc = create_doc("Document name", ".pdf")

    with open("documents/tests/files/3pages.pdf", "rb") as fd:
        f = File(fd)
        doc.pdf.save("another-uuid-beef-dead.pdf", f)

    result = tasks.mesure_pdf_length.delay(doc.id)
    assert result.status == celery.states.SUCCESS, result.traceback

    doc = Document.objects.get(id=doc.id)  # Get back the updated instance
    assert doc.pages == 3


def test_finish_file():
    doc = create_doc("Document name", ".pdf")

    result = tasks.finish_file.delay(doc.id)
    assert result.status == celery.states.SUCCESS, result.traceback

    doc = Document.objects.get(id=doc.id)  # Get back the updated instance
    assert doc.state == Document.DocumentState.DONE


def test_repair():
    doc = create_doc("Document name", ".pdf")

    with open("documents/tests/files/broken.pdf", "rb") as fd:
        f = File(fd)
        doc.pdf.save("another-uuid-beef-yolo.pdf", f)

    old_path = doc.pdf.path

    # Magic number of a PDF should be "%PDF" but the broken pdf has "PDF"
    # (missing "%")
    with doc.pdf.open() as fd:
        assert fd.read(3) == b"PDF"

    result = tasks.repair.delay(doc.id)
    assert result.status == celery.states.SUCCESS, result.traceback

    doc = Document.objects.get(pk=doc.id)

    # File should be repaired
    with doc.pdf.open() as fd:
        assert fd.read(4) == b"%PDF"

    assert old_path != doc.pdf.path


def test_repairs_original_too():
    doc = create_doc("Document name", ".pdf")

    with open("documents/tests/files/broken.pdf", "rb") as fd:
        f = File(fd)
        doc.original.save("another-uuid-beef-yolo.pdf", f)

    doc.pdf = doc.original
    doc.save()

    # Magic number of a PDF should be "%PDF" but the broken pdf has "PDF"
    # (missing "%")
    with doc.pdf.open() as fd:
        assert fd.read(3) == b"PDF"

    result = tasks.repair.delay(doc.id)
    assert result.status == celery.states.SUCCESS, result.traceback

    doc = Document.objects.get(pk=doc.id)

    # File should be repaired
    with doc.pdf.open() as fd:
        assert fd.read(4) == b"%PDF"

    with doc.original.open() as fd:
        assert fd.read(4) == b"%PDF"


def test_thumbnail():
    doc = create_doc("Document name2", ".pdf")

    with open("documents/tests/files/3pages.pdf", "rb") as fd:
        f = File(fd)
        doc.pdf.save("another-uuid-beef-dead.pdf", f)

    tasks.process_thumbnail.delay(doc.id)

    doc = Document.objects.get(id=doc.id)  # Get back the updated instance
    assert doc.thumbnail.name
