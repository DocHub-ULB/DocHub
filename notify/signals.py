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
from notify.tasks import propagate_notification


def pre_notif_save(**kwargs):
    assert kwargs['sender'] == models.PreNotification
    pre_notif = kwargs['instance']

    if kwargs['created'] and not pre_notif.delivered:
        propagate_notification.delay(pre_notif.id)
