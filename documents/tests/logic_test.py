from io import BytesIO

import pytest

from catalog.models import Course
from documents import logic
from documents.models import Document
from tags.models import Tag
from users.models import User

pytestmark = pytest.mark.django_db


@pytest.fixture
def user():
    return User.objects.create_user(netid="test_user")


@pytest.fixture
def course():
    return Course.objects.create(slug="test-t-100")


def test_add_file_to_course(user, course):
    Tag.objects.create(name="tag one")
    tags = ["tag one", "tag two", Tag.objects.create(name="tag three")]

    file = BytesIO(b"mybinarydocumentcontent")
    file.size = len(b"mybinarydocumentcontent")

    doc = logic.add_file_to_course(file, "My document", ".dll", course, tags, user)

    assert doc
    assert doc in course.document_set.all()
    assert doc.name == "My document"
    assert doc.state == Document.DocumentState.READY_TO_QUEUE
    assert Tag.objects.count() == 3
    assert doc.tags.count() == 3
    assert doc.file_type == ".dll"


def test_no_extension(user, course):
    doc = b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\n/\x00\x00\t\x81\x08\x06\x00\x00\x00'\x06\xfee\x00\x00\x00\tpHYs\x00\x00n\xba\x00\x00n\xba\x01\xd6\xde\xb1\x17\x00\x00\x00\x19tEXtSoftware\x00www.inkscape.org\x9b\xee<\x1a\x00\x00 \x00IDATx"
    file = BytesIO(doc)
    file.size = len(doc)

    doc = logic.add_file_to_course(file, "My document", "", course, [], user)

    assert doc
    assert doc.file_type == ".png"
