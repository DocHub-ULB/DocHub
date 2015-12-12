# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import pytest
from telepathy.models import Thread
from users.models import User
from catalog.models import Course
import json

pytestmark = pytest.mark.django_db


def create_thread(name):
    course = Course.objects.create(slug='AAA-000')
    user = User.objects.create_user(netid='test_user')
    thread = Thread.objects.create(name=name, user=user, course=course)

    return thread


def test_page_no_none():
    thread = create_thread('coucou')
    assert thread.page_no is None


def test_page_no():
    thread = create_thread('coucou')
    thread.placement = json.dumps({'page-no': 100})
    assert thread.page_no is 100
