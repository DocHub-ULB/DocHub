import pytest
from unittest import mock
import sys

from django.core.files import File

from users.models import User
from documents.models import Document
from documents.models import process_document
from celery_test import create_doc

pytestmark = pytest.mark.django_db


@pytest.fixture(scope='function')
def doc():
    user = User.objects.create_user(netid='test_user')
    doc = Document.objects.create(name='A document', user=user)

    return doc


def test_repr(doc):
    doc.name = "Coucou"
    r = repr(doc)

    if sys.version_info.major < 3:
        r = r.decode('utf-8')

    assert r == '<Document: Coucou>'


def test_repr_with_accents(doc):
    doc.name = "Lés accênts c'est cool"
    r = repr(doc)

    if sys.version_info.major < 3:
        r = r.decode('utf-8')

    assert r == "<Document: Lés accênts c'est cool>"


def test_url(doc):
    assert doc.get_absolute_url() == f"/documents/{doc.id}"


def test_tag_from_name_exam(doc):
    doc.name = "Examen (corrigé)"
    doc.tag_from_name()
    assert set(map(lambda x: x.name, doc.tags.all())) == {'examen', 'corrigé'}


def test_tag_from_name_exam_month(doc):
    doc.name = "Mai 2012"
    doc.tag_from_name()
    assert set(map(lambda x: x.name, doc.tags.all())) == {'examen'}


def test_tag_resume(doc):
    doc.name = "Résumé de Nicolas"
    doc.tag_from_name()
    assert set(map(lambda x: x.name, doc.tags.all())) == {'résumé'}


@mock.patch.object(Document, 'add_to_queue')
def test_reprocess_done(mock_add_to_queue, doc):
    doc.state = Document.DocumentState.DONE

    with pytest.raises(Exception):
        doc.reprocess()
    assert mock_add_to_queue.called == 0


@mock.patch.object(Document, 'add_to_queue')
def test_reprocess(mock_add_to_queue, doc):
    doc.state = Document.DocumentState.ERROR
    doc.reprocess()

    assert mock_add_to_queue.called == 1


@mock.patch.object(process_document, 'delay')
def test_add_to_queue(mock_process_document, doc):
    doc.state = 'ANYTHING'

    doc.add_to_queue()

    assert doc.state == Document.DocumentState.IN_QUEUE
    assert mock_process_document.called == 1


def test_document_file_cleanup():
    doc = create_doc('TestDocumentToDelete', '.pdf') # from celery tests
    doc.save()

    with open('documents/tests/files/3pages.pdf', 'rb') as fd:
        f = File(fd)
        doc.pdf.save('ThisPdfShouldGetDeleted.pdf', f)
        doc.original.save("ThisOriginalShouldGetDeleted.pdf", f)

    # Get file paths
    originalfilename = doc.original.file.name
    pdffilename = doc.pdf.file.name

    doc.delete()
    with pytest.raises(IOError) as errorinfo:
        open(originalfilename)
    assert 'No such file or directory' in str(errorinfo)

    with pytest.raises(IOError) as errorinfo:
        open(pdffilename)
    assert 'No such file or directory' in str(errorinfo)
