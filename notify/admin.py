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
from notify.models import PreNotification, Notification


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    readonly_fields = (
        'user',
        'node',
        'prenotif',
    )

    list_display = ('id', 'prenotif', 'user', 'node', 'read')
    list_filter = ('read',)


@admin.register(PreNotification)
class PreNotificationAdmin(admin.ModelAdmin):
    readonly_fields = (
        'node',
        'url',
    )

    list_display = ('id', 'text', 'delivered', 'user', 'personal')
    list_filter = ('delivered', 'personal')
