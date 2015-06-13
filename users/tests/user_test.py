# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import pytest
from users.models import User
from www import settings

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
    u = User.objects.create(first_name="Jean", last_name="DuJardin")
    assert u.name == "Jean DuJardin"


def test_default_photo():
    u = User.objects.create(netid="glagaffe")
    assert u.get_photo == User.DEFAULT_PHOTO


def test_photo():
    u = User.objects.create_user(netid="glagaffe", email="a@dupis.be")
    assert u.photo == 'png'
    assert u.get_photo == settings.MEDIA_URL + "profile/glagaffe.png"
