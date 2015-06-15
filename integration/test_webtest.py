# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import django_webtest
from users.models import User
from catalog.models import Category, Course

from django.core.urlresolvers import reverse
import pytest

pytestmark = [pytest.mark.django_db, pytest.mark.webtest]


@pytest.fixture(scope='function')
def app(request):
    wtm = django_webtest.WebTestMixin()
    wtm._patch_settings()
    request.addfinalizer(wtm._unpatch_settings)
    return django_webtest.DjangoTestApp()


@pytest.fixture(scope='function')
def user():
    return User.objects.create_user(
        netid='nimarcha',
        email="lol@lol.be",
        first_name="Nikita",
        last_name="Marchant"
    )


@pytest.fixture(scope='function')
def tree():
    root = Category.objects.create(name="ULB")
    science = Category.objects.create(name="science", parent=root)
    swag = Course.objects.create(name="Optimization of algorithmical SWAG", slug="swag-h-042")
    swag.categories.add(science)

    return root


def test_full_name_in_page(app, user):
    index = app.get('/', user=user.netid)
    assert user.name in index


def test_follow(app, user, tree):
    index = app.get('/', user=user.netid)
    catalog = index.click(href=reverse("show_courses"), index=0)
    category = catalog.click(description="science")
    course = category.click(description=lambda x: "swag-h-042" in x)
    course = course.click(
        # description="S'abonner",
        href=reverse('join_course', args=("swag-h-042",)),
    ).follow()

    assert "Se désabonner" in course

    index = app.get('/', user=user.netid)
    assert "swag-h-042" in index

    course = course.click(
        href=reverse('leave_course', args=("swag-h-042",)),
    ).follow()

    index = app.get('/', user=user.netid)
    assert "swag-h-042" not in index
