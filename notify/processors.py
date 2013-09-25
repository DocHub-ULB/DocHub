# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from notify.models import Notification

def notify(request):
    if hasattr(request, 'user') and request.user.is_authenticated() :
        notifications = Notification.objects.filter(read=False,user=request.user)
        return {'notifcount':len(notifications) }
    return {}