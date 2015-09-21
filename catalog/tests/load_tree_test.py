# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.core.management import call_command
from catalog.models import Course, Category

import pytest


pytestmark = [pytest.mark.django_db]


def test_load_tree():
    call_command('loadtree')

    ulb = Category.objects.get(level=0)
    assert ulb.name == "ULB"

    bio = Course.objects.get(slug="biol-f-102")
    assert bio.name == "Bio générale"

    options = Category.objects.get(name="Options")
    assert options in bio.categories.all()


def test_empty_tree():
    category = Category.objects.create(name="Caca", slug="prout")
    course = Course.objects.create(name="Testing", slug="test-h-100")

    course.categories.add(category)

    call_command('loadtree')

    assert Category.objects.filter(slug="prout").count() == 0

    course = Course.objects.get(slug="test-h-100")
    assert course.categories.count() == 0


@pytest.mark.slow
@pytest.mark.network
def test_load_tree_hit_ulb():
    call_command('loadtree', hitulb=True)

    bio = Course.objects.get(slug="biol-f-102")
    assert bio.name == "Biologie générale"
