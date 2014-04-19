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

import models
from notify.models import PreNotification
from django.core.urlresolvers import reverse


def thread_save(**kwargs):
    assert kwargs['sender'] == models.Thread

    if kwargs['created']:
        thread = kwargs['instance']
        PreNotification.objects.create(
            node=thread,
            sender_type="Thread",
            text='Nouvelle discussion : "{}"'.format(thread.name),
            url=reverse('thread_show', args=[thread.id]),
            user=thread.user,
            icon="torsos",
        )


def message_save(**kwargs):
    assert kwargs['sender'] == models.Message

    message = kwargs['instance']
    thread = message.thread

    if kwargs['created']:
        if not message.thread.message_set.first() == message:
            PreNotification.objects.create(
                node=thread,
                sender_type="Message",
                sender_info=message.id,
                text='Réponse à "{}"'.format(thread.name),
                url=reverse('thread_show', args=[thread.id]) + "#message-" + str(message.id),
                user=message.user,
                icon="plus",
            )
