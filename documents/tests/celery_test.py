# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from documents.models import Document
from users.models import User
from documents.tasks import process_document, mutool_get_pages
from documents import tasks
from django.core.files import File
import celery
from subprocess import call
import signal

import pytest


pytestmark = [pytest.mark.django_db, pytest.mark.celery]


class Alarm(Exception):
    pass


def alarm_handler(signum, frame):
    raise Alarm


def start_unoconv():
    signal.signal(signal.SIGALRM, alarm_handler)
    signal.alarm(1)
    try:
        call(["unoconv", "--listener"]) # workaround for a shitty unoconv
        # Error: Unable to connect or start own listener. Aborting.
        # Setting a timeout because if a listener exists alreay it hangs...
    except Alarm:
        pass

    signal.alarm(0) # cancel alarm


def create_doc(name, ext):
    try:
        user = User.objects.get(netid='test_user')
    except User.DoesNotExist:
        user = User.objects.create_user(netid='test_user')
    doc = Document.objects.create(
        user=user,
        name=name,
        state="IN_QUEUE",
        file_type=ext
    )

    return doc


@pytest.mark.slow
def test_add_to_queue():

    doc = create_doc("Document name", ".pdf")
    f = File(open('documents/tests/files/3pages.pdf', 'rb'))
    doc.original.save("silly-unique-deadbeef-file.pdf", f)

    result = process_document.delay(doc.id)
    assert result.status == celery.states.SUCCESS, result.traceback

    doc = Document.objects.get(id=doc.id) # Get back the updated instance

    assert doc.state == "DONE"
    assert doc.original.path == doc.pdf.path


@pytest.mark.slow
def test_send_duplicate():
    test_add_to_queue()

    doc = create_doc("Document name2", ".pdf")

    f = File(open('documents/tests/files/3pages.pdf', 'rb'))
    doc.original.save("another-uuid-beef-dead.pdf", f)

    result = process_document.delay(doc.id)
    assert result.status == celery.states.FAILURE
    assert "ExisingChecksum" in result.traceback
    assert Document.objects.filter(id=doc.id).count() == 0


# TODO : mock unoconv and provide a fake pdf instead
@pytest.mark.unoconv
@pytest.mark.slow
def test_send_office():
    doc = create_doc("My office doc", ".docx")

    f = File(open('documents/tests/files/2pages.docx', 'rb'))
    doc.original.save("silly-unique-deadbeef-file.docx", f)

    start_unoconv()

    result = process_document.delay(doc.id)
    assert result.status == celery.states.SUCCESS, result.traceback

    doc = Document.objects.get(id=doc.id) # Get back the updated instance

    assert doc.state == "DONE"
    assert doc.original.path != doc.pdf.path


def test_correct_checksum():
    doc = create_doc("Document name2", ".pdf")

    f = File(open('documents/tests/files/3pages.pdf', 'rb'))
    doc.original.save("another-uuid-beef-dead.pdf", f)

    result = tasks.checksum.delay(doc.id)
    assert result.status == celery.states.SUCCESS, result.traceback

    doc = Document.objects.get(id=doc.id) # Get back the updated instance
    assert doc.md5 == "8be98044ac25f3050b121aceac618823"


def test_duplicate_checksum():
    doc = create_doc("Document name2", ".pdf")
    doc.md5 = "8be98044ac25f3050b121aceac618823"
    doc.save()

    duplicate = create_doc("Document name2", ".pdf")

    f = File(open('documents/tests/files/3pages.pdf', 'rb'))
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

    f = File(open('documents/tests/files/3pages.pdf', 'rb'))
    duplicate.original.save("another-uuid-beef-dead.pdf", f)

    result = tasks.checksum.delay(duplicate.id)
    assert result.status == celery.states.SUCCESS, result.traceback
    assert Document.objects.filter(id=duplicate.id).count() == 1
    assert Document.objects.filter(id=doc.id).count() == 0
    assert Document.objects.get(id=duplicate.id).md5 == "8be98044ac25f3050b121aceac618823"


def test_correct_mutool_length():
    doc = create_doc("Document name", ".pdf")

    f = File(open('documents/tests/files/3pages.pdf', 'rb'))
    doc.pdf.save("another-uuid-beef-dead.pdf", f)

    assert mutool_get_pages(doc) == 3


def test_correct_length():
    doc = create_doc("Document name", ".pdf")

    f = File(open('documents/tests/files/3pages.pdf', 'rb'))
    doc.pdf.save("another-uuid-beef-dead.pdf", f)

    result = tasks.mesure_pdf_length.delay(doc.id)
    assert result.status == celery.states.SUCCESS, result.traceback

    doc = Document.objects.get(id=doc.id) # Get back the updated instance
    assert doc.pages == 3


def test_finish_file():
    doc = create_doc("Document name", ".pdf")

    result = tasks.finish_file.delay(doc.id)
    assert result.status == celery.states.SUCCESS, result.traceback

    doc = Document.objects.get(id=doc.id) # Get back the updated instance
    assert doc.state == "DONE"


def test_repair():
    doc = create_doc("Document name", ".pdf")

    f = File(open('documents/tests/files/broken.pdf', 'rb'))
    doc.pdf.save("another-uuid-beef-yolo.pdf", f)
    old_path = doc.pdf.path

    # Magic number of a PDF should be "%PDF" but the broken pdf has "PDF"
    # (missing "%")
    doc.pdf.open()
    assert doc.pdf.read(3) == b"PDF"
    doc.pdf.close()

    result = tasks.repair.delay(doc.id)
    assert result.status == celery.states.SUCCESS, result.traceback

    doc = Document.objects.get(pk=doc.id)

    # File should be repaired
    doc.pdf.open()
    assert doc.pdf.read(4) == b"%PDF"
    doc.pdf.close()

    assert old_path != doc.pdf.path


def test_repairs_original_too():
    doc = create_doc("Document name", ".pdf")

    f = File(open('documents/tests/files/broken.pdf', 'rb'))
    doc.original.save("another-uuid-beef-yolo.pdf", f)
    doc.pdf = doc.original
    doc.save()

    # Magic number of a PDF should be "%PDF" but the broken pdf has "PDF"
    # (missing "%")
    doc.pdf.open()
    assert doc.pdf.read(3) == b"PDF"
    doc.pdf.close()

    result = tasks.repair.delay(doc.id)
    assert result.status == celery.states.SUCCESS, result.traceback

    doc = Document.objects.get(pk=doc.id)

    # File should be repaired
    doc.pdf.open()
    assert doc.pdf.read(4) == b"%PDF"
    doc.pdf.close()

    doc.original.open()
    assert doc.original.read(4) == b"%PDF"
    doc.original.close()
