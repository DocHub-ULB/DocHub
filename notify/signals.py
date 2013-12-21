# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import models
from notify.tasks import propagate_notification

def pre_notif_save(**kwargs):
    assert kwargs['sender'] == models.PreNotification
    pre_notif = kwargs['instance']

    if kwargs['created']:
    	propagate_notification.delay(pre_notif.id)




