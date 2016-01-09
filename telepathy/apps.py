# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.apps import AppConfig
from actstream import registry


class TelepathyConfig(AppConfig):
    name = 'telepathy'

    def ready(self):
        registry.register(self.get_model('Thread'))
        registry.register(self.get_model('Message'))
