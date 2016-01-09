# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.apps import AppConfig
from actstream import registry


class NotificationsConfig(AppConfig):
    name = 'notifications'

    def ready(self):
        registry.register(self.get_model('Notification'))
