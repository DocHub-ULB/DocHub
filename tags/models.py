# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.utils.encoding import python_2_unicode_compatible

from math import sin, pi


@python_2_unicode_compatible
class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)

    @property
    def color(self):
        return "#%02x%02x%02x" % tuple(
            abs(int(200 * sin(self.id + x * pi / 3))) for x in range(3))

    def __str__(self):
        return self.name
