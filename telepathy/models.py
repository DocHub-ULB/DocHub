# -*- coding: utf-8 -*-
from __future__ import unicode_literals


import json
from django.db import models
from django.utils.text import Truncator
from django.core.urlresolvers import reverse
from django.conf import settings


class Thread(models.Model):
    # Possible placement options
    PLACEMENT_OPTS = {'page-no': int}

    name = models.CharField(max_length=255)

    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    created = models.DateTimeField(auto_now_add=True)
    edited = models.DateTimeField(auto_now=True)
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

    @property
    def json_placement(self):
        return json.loads(self.placement)


    def get_absolute_url(self):
        return reverse('thread_show', args=(self.id, ))

    def write_perm(self, user, moderated_courses):
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
    edited = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return self.text

    def fullname(self):
        return "un message"
        return Truncator(self.__unicode__()).words(9)

    def get_absolute_url(self):
        return reverse('thread_show', args=(self.thread_id, )) + "#message-{}".format(self.id)

    def write_perm(self, user, moderated_courses):
        if user.id == self.user_id:
            return True

        if self.thread.course_id in moderated_courses:
            return True

        return False
