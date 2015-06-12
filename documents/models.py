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
from www import settings


class Document(models.Model):
    name = models.CharField(max_length=255)
    course = models.ForeignKey('catalog.Course', null=True)

    description = models.TextField(blank=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    tags = models.ManyToManyField('tags.Tag')
    created = models.DateTimeField(auto_now_add=True)
    edited = models.DateTimeField(auto_now=True, auto_now_add=True)

    size = models.PositiveIntegerField(null=True, default=0)
    words = models.PositiveIntegerField(null=True, default=0)
    pages = models.PositiveIntegerField(null=True, default=0)
    date = models.DateTimeField(auto_now_add=True)

    views = models.PositiveIntegerField(null=True, default=0)
    downloads = models.PositiveIntegerField(null=True, default=0)

    file_type = models.CharField(max_length=255, default='')
    original = models.FileField(upload_to='original_document')
    pdf = models.FileField(upload_to='pdf_document')

    state = models.CharField(max_length=20, default='PREPARING', db_index=True)
    md5 = models.CharField(max_length=32, default='', db_index=True)

    def __unicode__(self):
        return self.name

    def reprocess(self, force=False):
        if self.state != "ERROR" and not force:
            raise Exception("Document is not in error state it is " + self.state)

        for page in self.page_set.all():
            page.delete()

        self.state = 'READY_TO_QUEUE'
        self.md5 = ""
        self.save()
        add_document_to_queue(self)
        self.save()


class Page(models.Model):
    numero = models.IntegerField(db_index=True)
    document = models.ForeignKey(Document, db_index=True)

    bitmap_120 = models.ImageField(upload_to='page_120', width_field="height_120")
    bitmap_600 = models.ImageField(upload_to='page_600', width_field="height_600")
    bitmap_900 = models.ImageField(upload_to='page_900', width_field="height_900")

    height_120 = models.PositiveIntegerField(null=True, default=0)
    height_600 = models.PositiveIntegerField(null=True, default=0)
    height_900 = models.PositiveIntegerField(null=True, default=0)

    class Meta:
        ordering = ['numero']


class DocumentError(models.Model):
    document = models.ForeignKey(Document)
    task_id = models.CharField(max_length=255)
    exception = models.CharField(max_length=1000)
    traceback = models.TextField()

    def __unicode__(self):
        return "#" + self.exception

from documents.cycle import add_document_to_queue
