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
from polydag.behaviors import Leaf, OneParent
from django.db.models.signals import post_save
import signals
from www import settings


class Thread(Leaf, OneParent, Taggable):
    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    created = models.DateTimeField(auto_now_add=True, editable=False)

    def __unicode__(self):
        return "#{}: {}".format(self.id, self.name)

    class Meta:
        ordering = ['-created']


class Message(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    thread = models.ForeignKey(Thread)
    text = models.TextField()
    created = models.DateTimeField(auto_now_add=True, editable=False)

    def __unicode__(self):
        t = self.text
        if len(t) > 60:
            t = t[:57] + "..."
        return "#{}: {}".format(self.id, t)

post_save.connect(signals.thread_save, sender=Thread)
post_save.connect(signals.message_save, sender=Message)
