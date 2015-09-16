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
from django.utils.text import Truncator
from django.core.urlresolvers import reverse

from www import settings


class Thread(models.Model):
    # Possible placement options
    PLACEMENT_OPTS = {'page-no': int}

    name = models.CharField(max_length=255)

    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    created = models.DateTimeField(auto_now_add=True)
    edited = models.DateTimeField(auto_now=True, auto_now_add=True)
    placement = models.TextField(default="", blank=True)

    course = models.ForeignKey('catalog.Course')
    document = models.ForeignKey('documents.Document', null=True)

    def __unicode__(self):
        return self.name

    def fullname(self):
        return self.__unicode__()

    @property
    def page_no(self):
        if self.placement:
            placement = json.loads(self.placement)
            if 'page-no' in placement:
                return placement['page-no']
        return None

    def get_absolute_url(self):
        return reverse('thread_show', args=(self.id, ))

    def has_perm(self, user, moderated_courses):
        if user.id == self.user_id:
            return True

        if self.course_id in moderated_courses:
            return True

        return False

    class Meta:
        ordering = ['-created']


class Message(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    thread = models.ForeignKey(Thread, db_index=True)
    text = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    edited = models.DateTimeField(auto_now=True, auto_now_add=True)

    def __unicode__(self):
        return self.text

    def fullname(self):
        return Truncator(self.__unicode__()).words(9)

    def get_absolute_url(self):
        return reverse('thread_show', args=(self.thread_id, )) + "#message-{}".format(self.id)

    def has_perm(self, user, moderated_courses):
        if user.id == self.user_id:
            return True

        if self.thread.course_id in moderated_courses:
            return True

        return False
