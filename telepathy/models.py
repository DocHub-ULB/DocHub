# -*- coding: utf-8 -*-
from __future__ import unicode_literals

# Copyright 2012, hast. All rights reserved.
#
# This program is free software: you can redistribute it and/or modify it
# under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or (at
# your option) any later version.

from django.db import models
from polydag.models import Taggable
from polydag.behaviors import Leaf, OneParent
from django.db.models.signals import post_save
import signals
from www import settings


class Thread(Leaf, OneParent, Taggable):
    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    created = models.DateTimeField(auto_now_add=True, editable=False)

    class Meta:
        ordering = ['-created']


class Message(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    thread = models.ForeignKey(Thread)
    text = models.TextField()
    previous = models.ForeignKey('self', null=True, default=None)
    created = models.DateTimeField(auto_now_add=True, editable=False)

post_save.connect(signals.thread_save, sender=Thread)
post_save.connect(signals.message_save, sender=Message)
