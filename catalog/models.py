# -*- coding: utf-8 -*-
from __future__ import unicode_literals

# Copyright 2014, Cercle Informatique ASBL. All rights reserved.
#
# This program is free software: you can redistribute it and/or modify it
# under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or (at
# your option) any later version.
#
# This software was made by hast, C4, ititou and rom1 at UrLab (http://urlab.be): ULB's hackerspace

from django.db import models
from django.core.urlresolvers import reverse

from mptt.models import MPTTModel, TreeForeignKey


class Category(MPTTModel):
    name = models.CharField(max_length=255, db_index=True)
    slug = models.SlugField(db_index=True)
    description = models.TextField(blank=True, default='')
    parent = TreeForeignKey('self', null=True, blank=True, related_name='children', db_index=True)

    class MPTTMeta:
        order_insertion_by = ['name']

    class Meta:
        verbose_name_plural = "categories"
        ordering = ['id']

    def __unicode__(self):
        return self.name


class Course(models.Model):
    name = models.CharField(max_length=255, db_index=True)
    slug = models.SlugField(unique=True, db_index=True)
    description = models.TextField(blank=True, default='')
    categories = models.ManyToManyField(Category)

    class Meta:
        ordering = ['slug']

    def gehol_url(self):
        slug = self.slug.replace('-', '').upper()
        return "http://gehol.ulb.ac.be/gehol/Vue/HoraireCours.php?cours=%s" % (slug,)

    def get_absolute_url(self):
        return reverse('course_show', args=(self.slug, ))

    def __unicode__(self):
        return self.slug.upper()

    def fullname(self):
        return "{} ({})".format(self.name, self.slug.lower())
