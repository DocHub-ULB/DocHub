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

from polydag.models import Node
from django.db import models


class Course(Node):
    slug = models.SlugField(unique=True)
    description = models.TextField(null=True)

    class Meta:
        ordering = ['slug']

    def gehol_url(self):
        slug = self.slug.replace('-', '').upper()
        period = '21-36' if datetime.now().month <= 6 else '1-14'
        return "http://gehol.ulb.ac.be/gehol/#!/Course/%s/%s" % (slug, period)

    def __unicode__(self):
        return "{}: {}".format(self.slug.upper(), self.name)


class Category(Node):
    slug = models.SlugField()
    description = models.TextField(null=True)

    class Meta:
        verbose_name_plural = "categories"
        ordering = ['id']

    def subcategories(self):
        return self.children(only=[Category])

    def courses(self):
        return self.children(only=[Course])

    def __unicode__(self):
        return "#{}: {}".format(self.id, self.name)
