# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import pytest
from users.models import User
from django.conf import settings
from PIL import Image

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


def test_photo():
    u = User.objects.create_user(netid="glagaffe", email="a@dupis.be")
    assert u.photo == 'png'
    assert u.get_photo == settings.MEDIA_URL + "profile/glagaffe.png"


def test_identicons():
    gaston = User.objects.create_user(netid="glagaffe", email="a@dupis.be")
    labevue = User.objects.create_user(netid="blabevue", email="b@dupis.be")

    assert gaston.get_photo != labevue.get_photo
    assert Image.open('media/profile/glagaffe.png') != Image.open('media/profile/blabevue.png')
