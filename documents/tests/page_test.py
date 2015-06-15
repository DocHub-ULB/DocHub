# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import pytest
from document_test import create_doc, add_pages
pytestmark = pytest.mark.django_db


def test_url():
    doc = create_doc("wtf")
    add_pages(doc)

    page = doc.page_set.first()
    assert page.get_absolute_url() == doc.get_absolute_url() + "#page-0"
