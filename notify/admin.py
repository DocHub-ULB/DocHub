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

from django.contrib import admin
from .models import PreNotification, Notification


class NotificationAdmin(admin.ModelAdmin):
    readonly_fields = (
        'user',
        'node',
        'prenotif'
    )

class PreNotificationAdmin(admin.ModelAdmin):
    readonly_fields = (
        'node',
    )

admin.site.register(PreNotification, PreNotificationAdmin)
admin.site.register(Notification, NotificationAdmin)
