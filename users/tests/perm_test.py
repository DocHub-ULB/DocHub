# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import pytest
from users.models import User
from catalog.models import Category, Course
from documents.models import Document

pytestmark = pytest.mark.django_db


@pytest.fixture(scope='function')
def tree():
    root = Category.objects.create(name="ULB")
    science = Category.objects.create(name="science", parent=root)

    swag = Course.objects.create(name="Optimization of algorithmical SWAG", slug="swag-h-042")
    swag.categories.add(science)

    yolo = Course.objects.create(name="Yolo as new life manager", slug="yolo-f-101")
    yolo.categories.add(science)

    return root


@pytest.fixture(scope='function')
def user():
    return User.objects.create_user(
        netid='myuser',
        email="myuser@lol.be",
        first_name="My",
        last_name="User"
    )


@pytest.fixture(scope='function')
def other_user():
    return User.objects.create_user(
        netid='otheruser',
        email="otheruser@lol.be",
        first_name="OtherU",
        last_name="ser"
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


def test_moderator(user, other_user, tree):
    course = Course.objects.last()
    user.moderated_courses.add(course)

    doc = Document.objects.create(user=other_user, course=course)
    assert user.write_perm(doc)


def test_bad_moderator(user, other_user, tree):
    course = Course.objects.last()
    other_course = Course.objects.first()
    assert course.id != other_course.id

    user.moderated_courses.add(course)

    doc = Document.objects.create(user=other_user, course=other_course)
    assert not user.write_perm(doc)


# TODO : do the same for threads and messages
