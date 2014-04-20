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

from datetime import datetime


def current_year():
    now = datetime.today()
    if datetime(now.year, 1, 1) < now < datetime(now.year, 9, 14):
        return now.year - 1
    else:
        return now.year


def year_choices():
    choices = []
    year = datetime.now().year
    if datetime.now().month >= 9 and datetime.now().day > 10:
        year -= 1
    for i in range(5):
        year -= 1
        s = "{}-{}".format(year, year + 1)
        choices.append((s, s))
    s = "Archives"
    choices.append((s, s))

    return choices
