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
from polydag.models import Node
from users.models import User


class PreNotification(models.Model):
    created = models.DateTimeField(auto_now=True)
    node = models.ForeignKey(Node, db_index=True)  # The node that initiated the notif
    text = models.CharField(max_length=160)
    sender_type = models.CharField(max_length=160)
    sender_info = models.CharField(max_length=160, default='')
    delivered = models.BooleanField(default=False, db_index=True)
    url = models.URLField()
    user = models.ForeignKey(User)  # The user that created the notification
    personal = models.BooleanField(default=False, db_index=True)
    icon = models.CharField(max_length=50, default="megaphone")


class Notification(models.Model):
    user = models.ForeignKey(User, db_index=True)
    node = models.ForeignKey(Node, db_index=True)  # The effective node followed by user
    prenotif = models.ForeignKey(PreNotification, db_index=True)
    read = models.BooleanField(default=False, db_index=True)
