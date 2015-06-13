# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from documents.models import Document
from users.models import User
from documents.tasks import process_document
from django.core.files import File
import celery
from subprocess import call
import signal

import pytest


pytestmark = pytest.mark.django_db


class Alarm(Exception):
    pass


def alarm_handler(signum, frame):
    raise Alarm


def start_unoconv():
    signal.signal(signal.SIGALRM, alarm_handler)

    try:
        call(["unoconv", "--listener"]) # workaround for a shitty unoconv
        # Error: Unable to connect or start own listener. Aborting.
        # Setting a timeout because if a listener exists alreay it hangs...
    except Alarm:
        pass

    signal.alarm(0) # cancel alarm


@pytest.mark.slow
def test_add_to_queue():
    user = User.objects.create(netid='test_user')

    doc = Document.objects.create(
        user=user,
        name="Document name",
        state="IN_QUEUE",
        file_type='.pdf'
    )

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

    user = User.objects.create(netid='test_user2', email="lol@lol.com")

    doc = Document.objects.create(
        user=user,
        name="Document name2",
        state="IN_QUEUE",
        file_type='.pdf'
    )

    f = File(open('documents/tests/files/3pages.pdf'))
    doc.original.save("another-uuid-beef-dead.pdf", f)

    result = process_document.delay(doc.id)
    assert result.status == celery.states.FAILURE
    assert "ExisingChecksum" in result.traceback
    assert Document.objects.filter(id=doc.id).count() == 0


@pytest.mark.slow
def test_send_office():
    user = User.objects.create(netid='test_user')

    doc = Document.objects.create(
        user=user,
        name="My office doc",
        state="IN_QUEUE",
        file_type='.docx'
    )

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
