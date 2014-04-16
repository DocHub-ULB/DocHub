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
from django.db.models.signals import post_save

import signals

# 1. Event occurs in graph
# 2. Pre notif created
# 3. Notif daemon match against followers and create notif
# 4. User get notif and read it


class PreNotification(models.Model):
    created = models.DateTimeField(auto_now=True)
    node = models.ForeignKey(Node)  # The node that initiated the notif
    text = models.CharField(max_length=160)
    sender_type = models.CharField(max_length=160)
    sender_info = models.CharField(max_length=160, default='')
    delivered = models.BooleanField(default=False)
    url = models.URLField()
    user = models.ForeignKey(User)  # The user that created the notification
    personal = models.BooleanField(default=False)

    def __unicode__(self):
        return self.text

    def content(self):
        if self.sender_type == "Thread":
            return self.node.message_set.first().text
        elif self.sender_type == "Message":
            message_id = int(self.sender_info)
            return Message.objects.get(id=message_id).text
        else:
            return ""


class Notification(models.Model):
    user = models.ForeignKey(User)
    node = models.ForeignKey(Node)  # The effective node followed by user
    prenotif = models.ForeignKey(PreNotification)
    read = models.BooleanField(default=False)

    @staticmethod
    def direct(user, text, node, url=None):
        """Directly deliver a single notification to a user"""
        Notification.objects.create(
            prenotif=PreNotification.objects.create(
                node=node,
                text=text,
                user=user,
                url=url,
                delivered=True,
                personal=True
            ),
            user=user,
            node=node
        )

    @staticmethod
    def unread(user):
        """Return all unread notifications for user"""
        return Notification.objects.filter(user=user, read=False)

    def __unicode__(self):
        return "Notification to {}".format(self.user)


post_save.connect(signals.pre_notif_save, sender=PreNotification)

from telepathy.models import Message, Thread
