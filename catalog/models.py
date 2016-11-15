# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.core.urlresolvers import reverse
from django.utils.encoding import python_2_unicode_compatible

from mptt.models import MPTTModel, TreeForeignKey


@python_2_unicode_compatible
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

    def __str__(self):
        return self.name


@python_2_unicode_compatible
class Course(models.Model):
    name = models.CharField(max_length=255, db_index=True)
    slug = models.SlugField(unique=True, db_index=True)
    categories = models.ManyToManyField(Category)

    class Meta:
        ordering = ['slug']

    def gehol_url(self):
        slug = self.slug.replace('-', '').upper()
        return "http://gehol.ulb.ac.be/gehol/Vue/HoraireCours.php?cours=%s" % (slug,)

    def get_absolute_url(self):
        return reverse('course_show', args=(self.slug, ))

    def __str__(self):
        return self.slug.upper()

    def fullname(self):
        return "{} ({})".format(self.name, self.slug.lower())
