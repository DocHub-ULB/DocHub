# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.http import HttpResponse, HttpResponseRedirect, HttpResponseForbidden
from django.shortcuts import get_object_or_404, render
from json import dumps, loads
from notify.models import Notification
from django.core.urlresolvers import reverse

def jsonise_notifications(notifs):
    return {
        "notifs": [
            {'id': n.pk,
             'text': n.prenotif.text,
             'date': n.prenotif.created.isoformat(),
             'emitter': n.prenotif.node.id,
             'followed_node': n.node.id,
             'read': n.read
            } for n in notifs
        ]
    }


def notifications_get(request):
    notifs = list(Notification.unread(request.user))
    if len(notifs) < 5:
        notifs += list(Notification.objects.filter(user=request.user, read=True)[:(5-len(notifs))])
    return HttpResponse(dumps(jsonise_notifications(notifs)), mimetype='application/json')

def notification_ajax_read(request, id):
    return notification_read(request, id, False)

def notification_read_all(request):
    Notification.objects.filter(user=request.user, read=False).update(read=True)
    return HttpResponseRedirect(reverse("notif_show"))

def notification_read(request, id, redirect=True):
    notif = get_object_or_404(Notification, id=id)
    if notif.user != request.user:
        return HttpResponseForbidden("This notification doesn't belong to you !")
    notif.read=True
    notif.save()
    if notif.prenotif.url:
        if redirect:
            return HttpResponseRedirect(notif.prenotif.url)
        else:
            return HttpResponse('Notification setted as read.')
    else :
        return HttpResponse('No url for this notification')


def notifications_show(request):
    notifs = list(Notification.unread(request.user).order_by('-id'))
    read_notifs = list(Notification.objects.filter(user=request.user, read=True).order_by('-id')[:5])

    context = {"notifications": notifs, 'read_notifications': read_notifs}
    return render(request, "notifications.html", context)

