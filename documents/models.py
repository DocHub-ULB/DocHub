# -*- coding: utf-8 -*-
from __future__ import unicode_literals

# Copyright 2012, hast. All rights reserved.
#
# This program is free software: you can redistribute it and/or modify it
# under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or (at
# your option) any later version.

from django.db import models
from users.models import Profile
from polydag.models import Taggable
from polydag.behaviors import OneParent

class Document(OneParent, Taggable):
    description = models.TextField()
    user = models.ForeignKey(Profile)

    size = models.PositiveIntegerField(null=True, default=0)
    words = models.PositiveIntegerField(null=True, default=0)
    pages = models.PositiveIntegerField(null=True, default=0)
    date = models.DateTimeField(auto_now_add=True)

    views = models.PositiveIntegerField(null=True, default=0)
    downloads = models.PositiveIntegerField(null=True, default=0)

    staticfile = models.CharField(max_length=2048, default='')
    source = models.CharField(max_length=2048, default='')
    state = models.CharField(max_length=10, default='pending')


    def move(self, *args, **kwargs):
        # Must move a images and associated files
        # thus NotImplementedError
        raise NotImplementedError
        super(Document,self).move(*args, **kwargs)


class Page(OneParent, Taggable):
    numero = models.IntegerField()
    height_120 = models.IntegerField()
    height_600 = models.IntegerField()
    height_900 = models.IntegerField()

    def move(self,newparent):
        # You may not move a page from a document to another
        raise NotImplementedError