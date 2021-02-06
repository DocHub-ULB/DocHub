import os
import tempfile
from unittest import mock

from django.conf import settings
from django.core.management import call_command

import pytest

from catalog.models import Course
from documents.models import Document
from users.models import User

pytestmark = pytest.mark.django_db


@mock.patch.object(Document, 'add_to_queue')
def test_importer(mock_add_to_queue):
    User.objects.create_user(netid='test_user')
    Course.objects.create(slug="test-t-100")

    tmpdir = tempfile.mkdtemp()
    src = os.path.join(settings.BASE_DIR, "documents/tests/files/3pages.pdf")
    dst = os.path.join(tmpdir, "off,ref,invalid_tag:My_Doc.pdf")
    os.symlink(src, dst)

    call_command('import_documents', username="test_user", course_slug="test-t-100", path=tmpdir)

    assert mock_add_to_queue.called == 1
    doc = Document.objects.last()

    assert doc.name == "My Doc"
    assert doc.tags.count() == 2
    assert doc.course.slug == 'test-t-100'
    assert doc.user.netid == "test_user"


@mock.patch.object(Document, 'add_to_queue')
def test_importer_with_no_tags(mock_add_to_queue):
    User.objects.create_user(netid='test_user')
    Course.objects.create(slug="test-t-100")

    tmpdir = tempfile.mkdtemp()
    src = os.path.join(settings.BASE_DIR, "documents/tests/files/3pages.pdf")
    dst = os.path.join(tmpdir, "doc corrigé with no_tags.pdf")
    os.symlink(src, dst)

    call_command('import_documents', username="test_user", course_slug="test-t-100", path=tmpdir)

    assert mock_add_to_queue.called == 1
    doc = Document.objects.last()

    assert doc.name == "doc corrigé with no tags"
    assert doc.tags.count() == 1
    assert doc.course.slug == 'test-t-100'
    assert doc.user.netid == "test_user"
