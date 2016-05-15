# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.apps import AppConfig


class TagsConfig(AppConfig):
    name = 'tags'

    def ready(self):
        from actstream import registry
        registry.register(self.get_model('Tag'))
