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

import os
import shutil

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

    original = models.CharField(max_length=2048, default='')
    pdf = models.CharField(max_length=2048, default='')

    state = models.CharField(max_length=20, default='PREPARING')
    md5 = models.CharField(max_length=32, default='')

    def move(self, *args, **kwargs):
        # Must move a images and associated files
        # thus NotImplementedError
        raise NotImplementedError
        super(Document, self).move(*args, **kwargs)

    def original_extension(self):
        return os.path.splitext(self.original)[1][1:].lower()

    def __unicode__(self):
        return "#{}: {}".format(self.id, self.name)

    def delete(self, *args, **kwargs):
        try:
            try:
                if self.original != "":
                    shutil.rmtree(os.path.dirname(self.original))
            except OSError:
                pass
            try:
                if self.pdf != "":
                    shutil.rmtree(os.path.dirname(self.pdf))
            except OSError:
                pass
        finally:
            super(Document, self).delete(*args, **kwargs)

    def _default_folder(self):
        return os.path.join(settings.UPLOAD_DIR, str(self.parent.id), "doc-{}".format(self.id))

    def _default_original_path(self, extension):
        return os.path.join(self._default_folder(), "original.{}".format(extension))


class Page(OneParent, Taggable):
    numero = models.IntegerField()
    height_120 = models.IntegerField()
    height_600 = models.IntegerField()
    height_900 = models.IntegerField()

    def move(self, newparent):
        raise NotImplementedError("You may not move a page from a document to another")
