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

from django.db import models
from polydag.models import Node
from graph.models import Course


class Event(Node):
    start = models.DateTimeField(auto_now=True)
    end = models.DateTimeField(auto_now=True)
    information = models.TextField()
