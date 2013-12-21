# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from graph.models import Course
from datetime import datetime

def gehol_url(course):
    assert(isinstance(course, Course))
    slug = course.slug.replace('-', '').upper()
    period = '21-36' if datetime.now().month <= 6 else '1-14'
    return "http://gehol.ulb.ac.be/gehol/#!/Course/%s/%s"%(slug, period)
