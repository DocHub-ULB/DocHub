# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.apps import AppConfig


class NotificationsConfig(AppConfig):
    name = 'notifications'

    def ready(self):
        from actstream import registry
        registry.register(self.get_model('Notification'))
