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

from polydag.models import Taggable
from polydag.behaviors import OneParent
from www import settings


class Document(OneParent, Taggable):

    description = models.TextField(blank=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL)

    size = models.PositiveIntegerField(null=True, default=0)
    words = models.PositiveIntegerField(null=True, default=0)
    pages = models.PositiveIntegerField(null=True, default=0)
    date = models.DateTimeField(auto_now_add=True)

    views = models.PositiveIntegerField(null=True, default=0)
    downloads = models.PositiveIntegerField(null=True, default=0)

    file_type = models.CharField(max_length=255, default='')
    original = models.FileField(upload_to='original_document')
    pdf = models.FileField(upload_to='pdf_document')

    state = models.CharField(max_length=20, default='PREPARING')
    md5 = models.CharField(max_length=32, default='')

    def move(self, *args, **kwargs):
        # Must move a images and associated files
        # thus NotImplementedError
        raise NotImplementedError

    def __unicode__(self):
        return "#{}: {}".format(self.id, self.name)

    @property
    def page_set(self):
        children = self.children()
        return children.instance_of(Page)

    def reprocess(self):
        if self.state != "ERROR":
            raise Exception("Document is not in error state it is " + self.state)

        for page in self.page_set.all():
            page.delete()

        self.state = 'READY_TO_QUEUE'
        self.md5 = ""
        self.save()
        add_document_to_queue(self)
        self.save()


class Page(OneParent, Taggable):
    numero = models.IntegerField()

    bitmap_120 = models.ImageField(upload_to='page_120', width_field="height_120")
    bitmap_600 = models.ImageField(upload_to='page_600', width_field="height_600")
    bitmap_900 = models.ImageField(upload_to='page_900', width_field="height_900")

    height_120 = models.PositiveIntegerField(null=True, default=0)
    height_600 = models.PositiveIntegerField(null=True, default=0)
    height_900 = models.PositiveIntegerField(null=True, default=0)

    def move(self, newparent):
        raise NotImplementedError("You may not move a page from a document to another")


class DocumentError(models.Model):
    document = models.ForeignKey(Document)
    task_id = models.CharField(max_length=255)
    exception = models.CharField(max_length=1000)
    traceback = models.TextField()

from documents.cycle import add_document_to_queue
