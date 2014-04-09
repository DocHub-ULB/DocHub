# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from __future__ import absolute_import

# Copyright 2014, Cercle Informatique ASBL. All rights reserved.
#
# This program is free software: you can redistribute it and/or modify it
# under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or (at
# your option) any later version.
#
# This software was made by hast, C4, ititou at UrLab, ULB's hackerspace

from celery import shared_task

import notify.models


@shared_task(bind=True)
def propagate_notification(self, notification_id):
    prenotif = notify.models.PreNotification.objects.get(pk=notification_id)

    notif_counter = 0
    nodeset = prenotif.node.ancestors_set()
    nodeset.add(prenotif.node)
    delivered = set()
    #Walk in ancestors graph
    for node in nodeset:
        #Deliver notifs to followers of ancestor nodes
        for follower in node.followed.all():
            if follower != prenotif.user and follower not in delivered:
                notif_counter += 1
                delivered.add(follower)  # avoid duplicate notifs
                notify.models.Notification.objects.create(
                    prenotif=prenotif,
                    user=follower,
                    node=node
                )
    prenotif.delivered = True
    prenotif.save()
