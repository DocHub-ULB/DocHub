import os

from django.conf import settings
from django.core.management import call_command

import pytest

from catalog.models import Category, Course

pytestmark = [pytest.mark.django_db]

fixtures = os.path.join(settings.BASE_DIR, 'catalog', 'tests', 'fixtures')
SIMPLE_TREE = os.path.join(fixtures, 'simple_tree.yaml')
MULTIPLE_TREE = os.path.join(fixtures, 'multiple_tree.yaml')
REAL_TREE = os.path.join(fixtures, 'real_tree.yaml')


def test_load_tree():
    call_command('loadtree', SIMPLE_TREE)

    ulb = Category.objects.get(level=0)
    assert ulb.name == "ULB"

    opti = Course.objects.get(slug="opti-f-1001")
    assert opti.categories.count() == 1
    options = opti.categories.last()

    assert options.name == "Options"
    assert options.level == 3


def test_load_multiple_tree():
    call_command('loadtree', MULTIPLE_TREE)

    info = Category.objects.get(name="Informatique")
    assert info.level == 1

    phys = Category.objects.get(name="Physique")
    assert phys.level == 1

    master = phys.children.first()
    assert master.name == "Master"
    assert master.course_set.count() == 1
    assert master.course_set.last().slug == "phys-h-200"


def test_empty_tree():
    category = Category.objects.create(name="Caca", slug="prout")
    course = Course.objects.create(name="Testing", slug="test-h-100")

    course.categories.add(category)

    call_command('loadtree', SIMPLE_TREE)

    assert Category.objects.filter(slug="prout").count() == 0

    course = Course.objects.get(slug="test-h-100")
    assert course.categories.count() == 0


def test_fill_twice():
    call_command('loadtree', SIMPLE_TREE)

    course = Course.objects.last()
    course.name = "Autre chose"
    course.save()

    call_command('loadtree', SIMPLE_TREE)

    new_course = Course.objects.get(slug=course.slug)
    assert new_course.id == course.id
    assert course.name == new_course.name


@pytest.mark.slow
@pytest.mark.network
def test_load_tree_hit_ulb():
    call_command('loadtree', REAL_TREE, hitulb=True)

    info = Course.objects.get(slug="info-f-101")
    assert info.name == "Programmation"
