import pytest

from documents.models import Document
from users.models import User

pytestmark = pytest.mark.django_db


@pytest.fixture
def user():
    return User.objects.create_user(
        netid="myuser", email="myuser@lol.be", first_name="My", last_name="User"
    )


@pytest.fixture
def other_user():
    return User.objects.create_user(
        netid="otheruser",
        email="otheruser@lol.be",
        first_name="OtherU",
        last_name="ser",
    )


def test_superuser(user, other_user):
    user.is_staff = True
    user.save()
    doc = Document.objects.create(user=other_user)
    assert user.write_perm(doc)


def test_other_user(user, other_user):
    doc = Document.objects.create(user=user)
    assert not other_user.write_perm(doc)


def test_owner(user):
    doc = Document.objects.create(user=user)
    assert user.write_perm(doc)


def test_moderator(user, other_user):
    user.is_moderator = True
    user.save()
    doc = Document.objects.create(user=other_user)
    assert user.write_perm(doc)


# TODO : do the same for threads and messages
