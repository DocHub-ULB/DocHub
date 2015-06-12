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

import json
from django.db import models
from www import settings


class Thread(models.Model):
    # Possible placement options
    PLACEMENT_OPTS = {'page-no': int}

    name = models.CharField(max_length=255)

    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    created = models.DateTimeField(auto_now_add=True, editable=False, db_index=True)
    edited = models.DateTimeField(auto_now_add=True, auto_now=True, editable=False, db_index=True)
    placement = models.TextField(null=True, default=None)

    course = models.ForeignKey('catalog.Course')
    document = models.ForeignKey('documents.Document', null=True)

    def __unicode__(self):
        return self.name

    @property
    def page_no(self):
        if self.placement:
            placement = json.loads(self.placement)
            if 'page-no' in placement:
                return placement['page-no']
        return None

    class Meta:
        ordering = ['-created']


class Message(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    thread = models.ForeignKey(Thread, db_index=True)
    text = models.TextField()
    created = models.DateTimeField(auto_now_add=True, editable=False, db_index=True)
    edited = models.DateTimeField(auto_now_add=True, auto_now=True, editable=False, db_index=True)

    def __unicode__(self):
        t = self.text
        if len(t) > 60:
            t = t[:57] + "..."
        return "#{}: {}".format(self.id, t)
