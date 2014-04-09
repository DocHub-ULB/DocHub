# -*- coding: utf-8 -*-
from __future__ import unicode_literals

# Copyright 2014, Cercle Informatique ASBL. All rights reserved.
#
# This program is free software: you can redistribute it and/or modify it
# under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or (at
# your option) any later version.
#
# This software was made by hast, C4, ititou at UrLab, ULB's hackerspace

from graph.models import Course
from datetime import datetime


def gehol_url(course):
    assert(isinstance(course, Course))
    slug = course.slug.replace('-', '').upper()
    period = '21-36' if datetime.now().month <= 6 else '1-14'
    return "http://gehol.ulb.ac.be/gehol/#!/Course/%s/%s" % (slug, period)
