# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import pytest

from django.core.files import File

from documents.models import Page
from document_test import doc, add_pages
from celery_test import create_doc
pytestmark = pytest.mark.django_db


def test_url(doc):
    add_pages(doc)

    page = doc.page_set.first()
    assert page.get_absolute_url() == doc.get_absolute_url() + "#page-0"

doc

def test_page_file_cleanup():
    doc = create_doc('TestDocumentToDelete', '.pdf') # from celery tests

    page = Page.objects.create(numero=999, document=doc)
    page.save()

    f = File(open('documents/tests/files/testimage.jpg', 'rb'))
    page.bitmap_120.save('This120ShouldGetDeleted.jpg', f)
    page.bitmap_600.save('This600ShouldGetDeleted.jpg', f)
    page.bitmap_900.save('This900ShouldGetDeleted.jpg', f)

    bitmap_120 = page.bitmap_120.file.name
    bitmap_600 = page.bitmap_120.file.name
    bitmap_900 = page.bitmap_120.file.name

    page.delete()
    with pytest.raises(IOError) as errorinfo:
        file = open(bitmap_120, 'r')
    assert 'No such file or directory' in str(errorinfo)

    with pytest.raises(IOError) as errorinfo:
        file = open(bitmap_600, 'r')
    assert 'No such file or directory' in str(errorinfo)

    with pytest.raises(IOError) as errorinfo:
        file = open(bitmap_900, 'r')
    assert 'No such file or directory' in str(errorinfo)