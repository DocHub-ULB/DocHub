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
    if now.month < 9 and now.day < 15:
        return now.year - 1
    else:
        return now.year


def year_choices(backlog=5):
    year = current_year()
    choices = [("%d-%d"%(year-i, year-i+1),)*2 for i in range(backlog)]
    choices.append(("Archives",)*2)
    return choices
