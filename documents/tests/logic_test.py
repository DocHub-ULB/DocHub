# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from users.models import User
from catalog.models import Course
from tags.models import Tag
import pytest
from documents import logic
import StringIO

pytestmark = pytest.mark.django_db


@pytest.fixture(scope='function')
def user():
    return User.objects.create_user(netid='test_user')


@pytest.fixture(scope='function')
def course():
    return Course.objects.create(slug="test-t-100")


def test_add_file_to_course(user, course):
    Tag.objects.create(name="tag one")
    tags = ["tag one", "tag two", Tag.objects.create(name="tag three")]

    file = StringIO.StringIO("mybinarydocumentcontent")
    file.size = len("mybinarydocumentcontent")

    doc = logic.add_file_to_course(
        file,
        "My document",
        ".dll",
        course,
        tags,
        user
    )

    assert doc
    assert doc in course.document_set.all()
    assert doc.name == "My document"
    assert doc.state == 'READY_TO_QUEUE'
    assert Tag.objects.count() == 3
    assert doc.tags.count() == 3
