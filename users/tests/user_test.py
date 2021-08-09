from django.conf import settings

import pytest
from PIL import Image

from users.models import User

pytestmark = pytest.mark.django_db


def test_create():
    u = User.objects.create_user(netid="glagaffe", email="a@dupis.be", comment="trop nul")
    assert u.netid == "glagaffe"
    assert u.email == "a@dupis.be"
    assert u.comment == "trop nul"
    assert u.is_staff is False


def test_create_superuser():
    u = User.objects.create_superuser(
        netid="glagaffe",
        email="a@dupis.be",
        password="azerty",
        comment="trop nul"
    )
    assert u.netid == "glagaffe"
    assert u.email == "a@dupis.be"
    assert u.comment == "trop nul"
    assert u.is_staff is True


def test_name():
    u = User.objects.create_user(netid="jeanduj", first_name="Jean", last_name="DuJardin")
    assert u.name == "Jean DuJardin"
