import pytest
from six import StringIO

from catalog.models import Course
from documents import logic
from documents.models import Document
from tags.models import Tag
from users.models import User

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

    file = StringIO("mybinarydocumentcontent")
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
    assert doc.state == Document.DocumentState.READY_TO_QUEUE
    assert Tag.objects.count() == 3
    assert doc.tags.count() == 3
