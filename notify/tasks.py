# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import

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
            user = follower.user
            if user != prenotif.user and user not in delivered:
                notif_counter += 1
                delivered.add(user)  # avoid duplicate notifs
                notify.models.Notification.objects.create(
                    prenotif=prenotif,
                    user=user,
                    node=node
                )
    prenotif.delivered = True
    prenotif.save()
