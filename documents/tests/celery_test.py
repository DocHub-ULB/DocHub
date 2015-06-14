# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from documents.models import Document
from users.models import User
from documents.tasks import process_document
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
    user = User.objects.get_or_create(netid='test_user')[0]
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
    f = File(open('documents/tests/files/3pages.pdf'))
    doc.original.save("silly-unique-deadbeef-file.pdf", f)

    result = process_document.delay(doc.id)
    assert result.status == celery.states.SUCCESS, result.traceback

    doc = Document.objects.get(id=doc.id) # Get back the updated instance

    assert doc.state == "DONE"
    assert doc.page_set.count() == 3
    assert doc.page_set.count() == doc.pages
    assert doc.original.path == doc.pdf.path


@pytest.mark.slow
def test_send_duplicate():
    test_add_to_queue()

    doc = create_doc("Document name2", ".pdf")

    f = File(open('documents/tests/files/3pages.pdf'))
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

    f = File(open('documents/tests/files/2pages.docx'))
    doc.original.save("silly-unique-deadbeef-file.docx", f)

    start_unoconv()

    result = process_document.delay(doc.id)
    assert result.status == celery.states.SUCCESS, result.traceback

    doc = Document.objects.get(id=doc.id) # Get back the updated instance

    assert doc.state == "DONE"
    assert doc.page_set.count() == 2
    assert doc.page_set.count() == doc.pages
    assert doc.original.path != doc.pdf.path


def test_correct_checksum():
    doc = create_doc("Document name2", ".pdf")

    f = File(open('documents/tests/files/3pages.pdf'))
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

    f = File(open('documents/tests/files/3pages.pdf'))
    duplicate.original.save("another-uuid-beef-dead.pdf", f)

    result = tasks.checksum.delay(duplicate.id)
    assert result.status == celery.states.FAILURE
    assert "ExisingChecksum" in result.traceback
    assert Document.objects.filter(id=duplicate.id).count() == 0
