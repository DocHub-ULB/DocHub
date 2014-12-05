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

from os.path import join

from django.db import models
from polydag.models import Node
from users.models import User
from django.db.models.signals import post_save

import signals
from www import settings

# 1. Event occurs in graph
# 2. Pre notif created
# 3. Notif daemon match against followers and create notif
# 4. User get notif and read it


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

    def __unicode__(self):
        return self.text

    def content(self):
        if self.sender_type == "Thread":
            return self.node.message_set.first().text
        elif self.sender_type == "Message":
            message_id = int(self.sender_info)
            return Message.objects.get(id=message_id).text
        elif self.sender_type == "Document":
            doc = self.node
            url = join(settings.MEDIA_URL, "documents/{}/doc-{}/images/000000_n.jpg".format(doc.parent.id, doc.id))
            return "[![{}]({})]({})".format(doc.name, url, self.url)
        else:
            return ""


class Notification(models.Model):
    user = models.ForeignKey(User, db_index=True)
    node = models.ForeignKey(Node, db_index=True)  # The effective node followed by user
    prenotif = models.ForeignKey(PreNotification, db_index=True)
    read = models.BooleanField(default=False, db_index=True)

    @staticmethod
    def direct(user, text, node, icon="list", url=None):
        """Directly deliver a single notification to a user"""
        Notification.objects.create(
            prenotif=PreNotification.objects.create(
                node=node,
                text=text,
                user=user,
                url=url,
                delivered=True,
                personal=True,
                icon=icon,
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
from documents.models import Document
