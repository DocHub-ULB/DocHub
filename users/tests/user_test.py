from django.urls import reverse

import pytest

from users.models import User

pytestmark = pytest.mark.django_db


def test_create():
    u = User.objects.create_user(
        netid="glagaffe", email="a@dupis.be", comment="trop nul"
    )
    assert u.netid == "glagaffe"
    assert u.email == "a@dupis.be"
    assert u.comment == "trop nul"
    assert u.is_staff is False


def test_create_superuser():
    u = User.objects.create_superuser(
        netid="glagaffe", email="a@dupis.be", password="azerty", comment="trop nul"
    )
    assert u.netid == "glagaffe"
    assert u.email == "a@dupis.be"
    assert u.comment == "trop nul"
    assert u.is_staff is True


def test_name():
    u = User.objects.create_user(
        netid="jeanduj", first_name="Jean", last_name="DuJardin"
    )
    assert u.name == "Jean DuJardin"


def test_moderator_banner_hide(client):
    user = User.objects.create_user(
        netid="moduser",
        email="mod@ulb.be",
        first_name="Mod",
        last_name="User",
        is_moderator=True,
    )
    client.force_login(user)

    response = client.post(reverse("moderator_banner_hide"))

    assert response.status_code == 302

    user.refresh_from_db()
    assert user.moderator_welcome_dismissed is True
