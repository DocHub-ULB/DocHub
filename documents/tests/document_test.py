# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from documents.models import Document, Page
from users.models import User
import pytest
import mock

from documents.models import process_document


pytestmark = pytest.mark.django_db


def create_doc(name):
    user = User.objects.create(netid='test_user')
    doc = Document.objects.create(name=name, user=user)

    return doc


def add_pages(doc):
    for i in range(5):
        doc.page_set.add(Page(numero=i))


def test_repr():
    doc = create_doc("Coucou")
    assert repr(doc).decode('utf-8') == '<Document: Coucou>'


def test_repr_with_accents():
    doc = create_doc("Lés accênts c'est cool")
    assert repr(doc).decode('utf-8') == "<Document: Lés accênts c'est cool>"


@mock.patch.object(Document, 'add_to_queue')
def test_reprocess_done(mock_add_to_queue):
    doc = create_doc("Coucou")
    doc.state = "DONE"
    add_pages(doc)

    with pytest.raises(Exception):
        doc.reprocess()
    assert mock_add_to_queue.called == 0
    assert doc.page_set.count() != 0


@mock.patch.object(Document, 'add_to_queue')
def test_reprocess(mock_add_to_queue):
    doc = create_doc("Coucou")
    doc.state = 'ERROR'
    add_pages(doc)
    doc.reprocess()

    assert mock_add_to_queue.called == 1
    assert doc.page_set.count() == 0


@mock.patch.object(process_document, 'delay')
def test_add_to_queue(mock_process_document):
    doc = create_doc("Coucou")
    doc.state = 'ANYTHING'

    doc.add_to_queue()

    assert doc.state == "IN_QUEUE"
    assert mock_process_document.called == 1
