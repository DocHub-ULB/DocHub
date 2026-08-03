import pytest

from catalog.models import Course
from documents.models import Document
from users.models import User


@pytest.fixture
def user():
    return User.objects.create_user(
        netid="test_user", first_name="Test", last_name="User"
    )


@pytest.fixture
def course():
    return Course.objects.create(name="Test Course", slug="test-course")


@pytest.fixture
def document(user, course):
    return Document.objects.create(
        name="Test Document",
        user=user,
        course=course,
        state=Document.DocumentState.DONE,
    )
