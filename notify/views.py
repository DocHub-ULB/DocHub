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

from json import dumps, loads

from django.http import HttpResponse, HttpResponseRedirect, HttpResponseForbidden
from django.shortcuts import get_object_or_404, render
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse

from notify.models import Notification


@login_required
def jsonise_notifications(notifs):
    return {
        "notifs": [
            {
                'id': n.pk,
                'text': n.prenotif.text,
                'date': n.prenotif.created.isoformat(),
                'emitter': n.prenotif.node.id,
                'followed_node': n.node.id,
                'read': n.read
            } for n in notifs
        ]
    }


@login_required
def notifications_get(request):
    notifs = list(Notification.unread(request.user))
    if len(notifs) < 5:
        notifs += list(Notification.objects.filter(user=request.user, read=True)[:(5 - len(notifs))])
    return HttpResponse(dumps(jsonise_notifications(notifs)), mimetype='application/json')


@login_required
def notification_ajax_read(request, id):
    return notification_read(request, id, False)


@login_required
def notification_read_all(request):
    Notification.objects.filter(user=request.user, read=False).update(read=True)
    return HttpResponseRedirect(reverse("notif_show"))


@login_required
def notification_read(request, id, redirect=True):
    notif = get_object_or_404(Notification, id=id)
    if notif.user != request.user:
        return HttpResponseForbidden("This notification doesn't belong to you !")
    notif.read = True
    notif.save()
    if notif.prenotif.url:
        if redirect:
            return HttpResponseRedirect(notif.prenotif.url)
        else:
            return HttpResponse('Notification setted as read.')
    else:
        return HttpResponse('No url for this notification')


@login_required
def notifications_show(request):
    unread_len = Notification.unread(request.user).count()
    s = unread_len + 20
    notifs = list(
        Notification.objects.filter(user=request.user).order_by('read','-id').select_related('prenotif')[:s]
    )
    read_notifs = notifs[unread_len:]
    notifs = notifs[:unread_len]


    context = {"notifications": notifs, 'read_notifications': read_notifs}
    return render(request, "notifications.html", context)
