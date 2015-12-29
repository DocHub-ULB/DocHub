# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from documents.models import Document, Page
from users.models import User
import pytest
import mock

from documents.models import process_document


pytestmark = pytest.mark.django_db


@pytest.fixture(scope='function')
def doc():
    user = User.objects.create_user(netid='test_user')
    doc = Document.objects.create(name='A document', user=user)

    return doc


def add_pages(doc):
    for i in range(5):
        doc.page_set.add(Page(numero=i))


def test_repr(doc):
    doc.name = "Coucou"
    assert repr(doc).decode('utf-8') == '<Document: Coucou>'


def test_repr_with_accents(doc):
    doc.name = "Lés accênts c'est cool"
    assert repr(doc).decode('utf-8') == "<Document: Lés accênts c'est cool>"


def test_url(doc):
    assert doc.get_absolute_url() == "/document/{}".format(doc.id)


def test_tag_from_name_exam(doc):
    doc.name = "Examen (corrigé)"
    doc.tag_from_name()
    assert set(map(lambda x: x.name, doc.tags.all())) == set(['examen', 'corrigé'])


def test_tag_from_name_exam_month(doc):
    doc.name = "Mai 2012"
    doc.tag_from_name()
    assert set(map(lambda x: x.name, doc.tags.all())) == set(['examen'])


def test_tag_resume(doc):
    doc.name = "Résumé de Nicolas"
    doc.tag_from_name()
    assert set(map(lambda x: x.name, doc.tags.all())) == set(['résumé'])


@mock.patch.object(Document, 'add_to_queue')
def test_reprocess_done(mock_add_to_queue, doc):
    doc.state = "DONE"
    add_pages(doc)

    with pytest.raises(Exception):
        doc.reprocess()
    assert mock_add_to_queue.called == 0
    assert doc.page_set.count() != 0


@mock.patch.object(Document, 'add_to_queue')
def test_reprocess(mock_add_to_queue, doc):
    doc.state = 'ERROR'
    add_pages(doc)
    doc.reprocess()

    assert mock_add_to_queue.called == 1
    assert doc.page_set.count() == 0


@mock.patch.object(process_document, 'delay')
def test_add_to_queue(mock_process_document, doc):
    doc.state = 'ANYTHING'

    doc.add_to_queue()

    assert doc.state == "IN_QUEUE"
    assert mock_process_document.called == 1
