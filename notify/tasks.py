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


def upper_nodes(node):
    """
    Go up in graph through threads and documents until we reach a course.
    """
    if node.classBasename() in ("Thread", "Document"):
        res = []
        for parent in node.parents():
            res += upper_nodes(parent)
        return res
    elif node.classBasename() == "Course":
        return [node]
    return []


def find_candidates(prenotif):
    """
    Return all nodes interested in a notification delivery for this
    prenotification.
    """
    node = prenotif.node
    if prenotif.sender_type == "Message":
        res = [node]
    else:
        res = upper_nodes(node)
    return set(res)


@shared_task(bind=True)
def propagate_notification(self, notification_id):
    prenotif = notify.models.PreNotification.objects.get(pk=notification_id)

    notif_counter = 0
    impacted_nodes = find_candidates(prenotif)
    delivered = set()

    for node in impacted_nodes:
        # Deliver notifs to followers of ancestor nodes
        if prenotif.sender_type == "Message" and not node.classBasename() == "Thread":
            # Do not propagate new messages on a thread if followed node is not a thread
            continue
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
