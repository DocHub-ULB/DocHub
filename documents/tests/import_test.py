# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from documents.models import Document
from catalog.models import Course
from users.models import User
import pytest
import mock
import tempfile
import os
from www.settings import BASE_DIR

from django.core.management import call_command


pytestmark = pytest.mark.django_db


@mock.patch.object(Document, 'add_to_queue')
def test_importer(mock_add_to_queue):
    User.objects.create(netid='test_user')
    Course.objects.create(slug="test-t-100")

    dir = tempfile.mkdtemp()
    src = os.path.join(BASE_DIR, "documents/tests/files/3pages.pdf")
    dst = os.path.join(dir, "off,ref:My_Doc.pdf")
    os.symlink(src, dst)

    call_command('import_documents', username="test_user", course_slug="test-t-100", path=dir)

    assert mock_add_to_queue.called == 1
    doc = Document.objects.last()

    assert doc.name == "My Doc"
    assert doc.tags.count() == 2
    assert doc.course.slug == 'test-t-100'
    assert doc.user.netid == "test_user"
